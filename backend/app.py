import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, Query, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from database import Base, engine, get_db, SessionLocal
from models import CompanyBrief
from schemas import BriefCreate, BriefUpdate, BriefOut
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# Ensure database tables exist
Base.metadata.create_all(bind=engine)

# Initialize FastMCP Server
mcp = FastMCP(
    name="MASCoT Company Intelligence",
    instructions=(
        "MASCoT is a company intelligence workspace for the paint and commercial coatings industry. "
        "Use these tools to store, retrieve, search, and update company briefs. "
        "Research, reasoning, qualification, and synthesis are performed by Claude outside MASCoT; "
        "MASCoT provides the persistent application storage, retrieval, and synchronisation layer."
    )
)
# Allow remote connections over Streamable HTTP from cloud domains (e.g. Render, Claude, Antigravity)
mcp.settings.transport_security = TransportSecuritySettings(enable_dns_rebinding_protection=False)

# Define MCP Tools
@mcp.tool()
async def create_company_brief(
    company_name: str,
    industry: str = "Paint / Construction",
    location: str = "",
    company_overview: str = "",
    potential_paint_requirements: str = "",
    project_signals: str = "",
    meeting_questions: str = "",
    next_steps: str = "",
    source_urls: str = ""
) -> dict:
    """Save a new company intelligence brief in MASCoT."""
    db = SessionLocal()
    try:
        brief = CompanyBrief(
            company_name=company_name.strip(),
            industry=industry.strip() if industry else "Paint / Construction",
            location=location.strip() if location else "",
            company_overview=company_overview.strip() if company_overview else "",
            potential_paint_requirements=potential_paint_requirements.strip() if potential_paint_requirements else "",
            project_signals=project_signals.strip() if project_signals else "",
            meeting_questions=meeting_questions.strip() if meeting_questions else "",
            next_steps=next_steps.strip() if next_steps else "",
            source_urls=source_urls.strip() if source_urls else ""
        )
        db.add(brief)
        db.commit()
        db.refresh(brief)
        out = BriefOut.model_validate(brief).model_dump(mode="json")
        return {
            "success": True,
            "id": out["id"],
            "brief": out,
            "message": f"Successfully created and saved brief for '{out['company_name']}' with ID {out['id']}."
        }
    except Exception as exc:
        return {"success": False, "error": type(exc).__name__, "detail": str(exc)}
    finally:
        db.close()

@mcp.tool()
async def get_company_brief(brief_id: int) -> dict:
    """Retrieve an individual company brief by its record ID."""
    db = SessionLocal()
    try:
        brief = db.get(CompanyBrief, brief_id)
        if not brief:
            return {"success": False, "error": "Not Found", "detail": f"Brief {brief_id} not found"}
        return BriefOut.model_validate(brief).model_dump(mode="json")
    finally:
        db.close()

@mcp.tool()
async def list_company_briefs(search: str = "") -> list[dict] | dict:
    """List saved briefs; optionally filter by search keyword."""
    db = SessionLocal()
    try:
        stmt = select(CompanyBrief).order_by(CompanyBrief.updated_at.desc())
        if search and search.strip():
            term = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    CompanyBrief.company_name.ilike(term),
                    CompanyBrief.industry.ilike(term),
                    CompanyBrief.location.ilike(term)
                )
            )
        briefs = list(db.scalars(stmt).all())
        return [BriefOut.model_validate(b).model_dump(mode="json") for b in briefs]
    finally:
        db.close()

@mcp.tool()
async def update_company_brief(
    brief_id: int,
    company_name: str | None = None,
    industry: str | None = None,
    location: str | None = None,
    company_overview: str | None = None,
    potential_paint_requirements: str | None = None,
    project_signals: str | None = None,
    meeting_questions: str | None = None,
    next_steps: str | None = None,
    source_urls: str | None = None
) -> dict:
    """Update fields on an existing company brief."""
    db = SessionLocal()
    try:
        brief = db.get(CompanyBrief, brief_id)
        if not brief:
            return {"success": False, "error": "Not Found", "detail": f"Brief {brief_id} not found"}
        fields = {
            "company_name": company_name,
            "industry": industry,
            "location": location,
            "company_overview": company_overview,
            "potential_paint_requirements": potential_paint_requirements,
            "project_signals": project_signals,
            "meeting_questions": meeting_questions,
            "next_steps": next_steps,
            "source_urls": source_urls
        }
        for k, v in fields.items():
            if v is not None:
                setattr(brief, k, v.strip() if isinstance(v, str) else v)
        brief.updated_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(brief)
        out = BriefOut.model_validate(brief).model_dump(mode="json")
        return {
            "success": True,
            "id": out["id"],
            "brief": out,
            "message": f"Successfully updated brief ID {brief_id} ('{out['company_name']}')."
        }
    finally:
        db.close()

# Prepare MCP Starlette Sub-application
mcp_sub_app = mcp.streamable_http_app()

# FastAPI application setup
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    # Start the Streamable HTTP session manager cleanly
    if hasattr(mcp_sub_app.router, "lifespan_context"):
        async with mcp_sub_app.router.lifespan_context(mcp_sub_app):
            yield
    else:
        yield

app = FastAPI(
    title="MASCoT – Company Intelligence API & MCP Server",
    description="Unified API & Model Context Protocol (MCP) server for MASCoT Company Intelligence Workspace.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS setup
cors_env = os.getenv("CORS_ORIGINS", "*")
if cors_env.strip() == "*":
    origins = ["*"]
else:
    origins = [o.strip() for o in cors_env.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", include_in_schema=False)
def root():
    return {
        "service": "MASCoT Company Intelligence Workspace",
        "status": "online",
        "rest_api": "/briefs",
        "documentation": "/docs",
        "health": "/health",
        "mcp_endpoint": "/mcp",
        "mcp_transport": "streamable-http"
    }

# Friendly browser info endpoint for /mcp when visited without MCP headers
@app.get("/mcp", include_in_schema=False)
async def mcp_browser_info(request: Request):
    accept = request.headers.get("accept", "")
    if "text/event-stream" not in accept:
        return JSONResponse({
            "service": "MASCoT Model Context Protocol (MCP) Server",
            "status": "online",
            "transport": "streamable-http",
            "protocol_version": "2024-11-05",
            "tools": ["create_company_brief", "get_company_brief", "list_company_briefs", "update_company_brief"],
            "instructions": "Connect via Claude Desktop or an MCP client using Streamable HTTP transport."
        })
    # If client accepts text/event-stream, pass to MCP sub app
    return await mcp_sub_app(request.scope, request.receive, request._send)

@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify API and database connectivity."""
    try:
        db.execute(select(1)).scalar()
        return {
            "status": "ok",
            "service": "mascot-api",
            "database": "connected",
            "mcp_endpoint": "/mcp"
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unreachable: {str(exc)}"
        )

@app.post("/briefs", response_model=BriefOut, status_code=status.HTTP_201_CREATED, tags=["Briefs"])
def create_brief(payload: BriefCreate, db: Session = Depends(get_db)):
    """Create a new company intelligence brief."""
    brief = CompanyBrief(**payload.model_dump())
    db.add(brief)
    db.commit()
    db.refresh(brief)
    return brief

@app.get("/briefs", response_model=list[BriefOut], tags=["Briefs"])
def list_briefs(
    q: str | None = Query(default=None, description="Search term across company name, industry, or location"),
    db: Session = Depends(get_db)
):
    """Retrieve all company intelligence briefs, optionally filtered by search query."""
    stmt = select(CompanyBrief).order_by(CompanyBrief.updated_at.desc())
    if q and q.strip():
        term = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                CompanyBrief.company_name.ilike(term),
                CompanyBrief.industry.ilike(term),
                CompanyBrief.location.ilike(term)
            )
        )
    return list(db.scalars(stmt).all())

@app.get("/briefs/{brief_id}", response_model=BriefOut, tags=["Briefs"])
def get_brief(brief_id: int, db: Session = Depends(get_db)):
    """Retrieve an individual company brief by its unique ID."""
    brief = db.get(CompanyBrief, brief_id)
    if not brief:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company brief with ID {brief_id} not found"
        )
    return brief

@app.patch("/briefs/{brief_id}", response_model=BriefOut, tags=["Briefs"])
def update_brief(brief_id: int, payload: BriefUpdate, db: Session = Depends(get_db)):
    """Update fields on an existing company brief."""
    brief = db.get(CompanyBrief, brief_id)
    if not brief:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company brief with ID {brief_id} not found"
        )

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        return brief

    for field, val in updates.items():
        if val is not None:
            setattr(brief, field, val)

    brief.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(brief)
    return brief

@app.delete("/briefs/{brief_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Briefs"])
def delete_brief(brief_id: int, db: Session = Depends(get_db)):
    """Delete an existing company brief."""
    brief = db.get(CompanyBrief, brief_id)
    if not brief:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company brief with ID {brief_id} not found"
        )
    db.delete(brief)
    db.commit()
    return None

# Mount MCP Streamable HTTP app directly into root to handle all POST/DELETE /mcp requests
app.mount("", mcp_sub_app)
