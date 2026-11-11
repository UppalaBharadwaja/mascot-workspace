import os
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import select, or_
from database import Base, engine, get_db
from models import CompanyBrief
from schemas import BriefCreate, BriefUpdate, BriefOut

# Ensure tables exist on load and in lifespan
Base.metadata.create_all(bind=engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(
    title="MASCoT – Company Intelligence API",
    description="Backend API for MASCoT Company Intelligence Workspace. Manages company briefs with no internal AI engine.",
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

@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """Health check endpoint to verify API and database connectivity."""
    try:
        # Simple test query to verify database connection
        db.execute(select(1)).scalar()
        return {"status": "ok", "service": "mascot-api", "database": "connected"}
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
