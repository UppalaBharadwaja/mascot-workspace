import os
import sys
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
PORT = int(os.getenv("PORT", "8001"))

# Initialize FastMCP Server
mcp = FastMCP(
    name="MASCoT Company Intelligence",
    instructions=(
        "MASCoT is a company intelligence workspace for the paint and commercial coatings industry. "
        "Use these tools to store, retrieve, search, and update company briefs. "
        "Research, reasoning, qualification, and synthesis are performed by Claude outside MASCoT; "
        "MASCoT provides the persistent application storage, retrieval, and synchronisation layer."
    ),
    host="0.0.0.0",
    port=PORT,
)

async def _request(method: str, path: str, **kwargs) -> dict:
    """Helper function to execute HTTP requests against the MASCoT backend REST API."""
    url = f"{BACKEND_URL}{path}"
    try:
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.request(method, url, **kwargs)
            
            if response.status_code == 404:
                return {
                    "success": False,
                    "error": "Not Found",
                    "detail": f"Resource at '{path}' was not found in MASCoT database."
                }
            if response.status_code == 422:
                return {
                    "success": False,
                    "error": "Validation Error",
                    "detail": response.text
                }
            
            response.raise_for_status()

            if response.status_code == 204:
                return {"success": True}

            data = response.json()
            return {"success": True, "data": data}
            
    except httpx.ConnectError:
        return {
            "success": False,
            "error": "Connection Failed",
            "detail": f"Could not connect to MASCoT backend API at {BACKEND_URL}. Ensure backend is running."
        }
    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "Timeout",
            "detail": f"Request to MASCoT backend timed out after 25 seconds."
        }
    except Exception as exc:
        return {
            "success": False,
            "error": type(exc).__name__,
            "detail": str(exc)
        }


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
    """
    Create and save a new company intelligence brief in MASCoT.

    Args:
        company_name: Name of the prospective company (e.g., 'ABC Infrastructure').
        industry: Target industry or sector (default: 'Paint / Construction').
        location: City, state, or country (e.g., 'Hyderabad, Telangana').
        company_overview: Summary of company activities, scale, and operational background.
        potential_paint_requirements: Possible coating, protective, or decorative paint requirements.
        project_signals: Recent tenders, construction projects, facility expansions, or hiring signals.
        meeting_questions: Strategic discovery questions to qualify the opportunity.
        next_steps: Recommended follow-up actions, timelines, and account owners.
        source_urls: Source citations, news links, and reference URLs (one per line).

    Returns:
        A dictionary containing success status, newly created record ID, and the saved company brief.
    """
    payload = {
        "company_name": company_name.strip(),
        "industry": industry.strip() if industry else "Paint / Construction",
        "location": location.strip() if location else "",
        "company_overview": company_overview.strip() if company_overview else "",
        "potential_paint_requirements": potential_paint_requirements.strip() if potential_paint_requirements else "",
        "project_signals": project_signals.strip() if project_signals else "",
        "meeting_questions": meeting_questions.strip() if meeting_questions else "",
        "next_steps": next_steps.strip() if next_steps else "",
        "source_urls": source_urls.strip() if source_urls else ""
    }

    res = await _request("POST", "/briefs", json=payload)
    if not res.get("success"):
        return {
            "success": False,
            "error": res.get("error"),
            "detail": res.get("detail")
        }

    brief = res["data"]
    return {
        "success": True,
        "id": brief["id"],
        "brief": brief,
        "message": f"Successfully created and saved brief for '{brief['company_name']}' with ID {brief['id']}."
    }


@mcp.tool()
async def get_company_brief(brief_id: int) -> dict:
    """
    Retrieve an individual company intelligence brief by its MASCoT record ID.

    Args:
        brief_id: The unique integer ID of the company brief in MASCoT.

    Returns:
        The complete company brief dictionary or an error message if not found.
    """
    res = await _request("GET", f"/briefs/{brief_id}")
    if not res.get("success"):
        return {
            "success": False,
            "error": res.get("error"),
            "detail": res.get("detail")
        }
    return res["data"]


@mcp.tool()
async def list_company_briefs(search: str = "") -> list[dict] | dict:
    """
    List company briefs saved in MASCoT, optionally filtered by keyword search.

    Args:
        search: Optional search term to filter briefs by company name, industry, or location.

    Returns:
        List of matching company brief records, ordered with most recently updated first.
    """
    params = {"q": search.strip()} if search and search.strip() else None
    res = await _request("GET", "/briefs", params=params)
    if not res.get("success"):
        return {
            "success": False,
            "error": res.get("error"),
            "detail": res.get("detail")
        }
    return res["data"]


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
    """
    Update specific fields on an existing MASCoT company intelligence brief.

    Args:
        brief_id: The unique integer ID of the brief to update.
        company_name: Updated company name (optional).
        industry: Updated industry (optional).
        location: Updated location (optional).
        company_overview: Updated company overview (optional).
        potential_paint_requirements: Updated paint requirements (optional).
        project_signals: Updated project signals (optional).
        meeting_questions: Updated meeting questions (optional).
        next_steps: Updated next steps (optional).
        source_urls: Updated source URLs (optional).

    Returns:
        A dictionary containing success status and the updated company brief record.
    """
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
    payload = {k: v.strip() if isinstance(v, str) else v for k, v in fields.items() if v is not None}

    if not payload:
        return {
            "success": False,
            "error": "No Fields Provided",
            "detail": "At least one field must be provided to update the company brief."
        }

    res = await _request("PATCH", f"/briefs/{brief_id}", json=payload)
    if not res.get("success"):
        return {
            "success": False,
            "error": res.get("error"),
            "detail": res.get("detail")
        }

    brief = res["data"]
    return {
        "success": True,
        "id": brief["id"],
        "brief": brief,
        "message": f"Successfully updated brief ID {brief_id} ('{brief['company_name']}')."
    }


if __name__ == "__main__":
    transport = "stdio" if "--stdio" in sys.argv or os.getenv("MCP_TRANSPORT") == "stdio" else "streamable-http"
    if transport == "streamable-http":
        print(f"Starting MASCoT MCP Server on http://0.0.0.0:{PORT}...")
        print(f"Connected MASCoT Backend API URL: {BACKEND_URL}")
        print(f"Streamable HTTP MCP Endpoint: http://localhost:{PORT}/mcp")
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")
