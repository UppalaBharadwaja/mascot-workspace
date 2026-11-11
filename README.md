# MASCoT – Company Intelligence Workspace

[![Architecture: Zero In-App AI](https://img.shields.io/badge/Architecture-Zero%20In--App%20AI-183e35.svg)](#architecture-principle)
[![Protocol: Model Context Protocol (MCP)](https://img.shields.io/badge/Protocol-Model%20Context%20Protocol-2e7a5c.svg)](#mcp-architecture)
[![Backend: FastAPI + SQLAlchemy](https://img.shields.io/badge/Backend-FastAPI%20%7C%20SQLAlchemy-blue.svg)](https://fastapi.tiangolo.com/)
[![Frontend: React + Vite](https://img.shields.io/badge/Frontend-React%20%7C%20Vite-green.svg)](https://vitejs.dev/)

> **Product & Tech Assignment Submission for Volopay's Founder's Office, Product & Growth Role.**  
> Built strictly adhering to the **Zero In-App AI** mandate: The customer connects their own Claude account via the Model Context Protocol (MCP); Claude performs all research, writing, and reasoning, while MASCoT provides the permanent application, persistence, editing, and synchronisation layer.

---

## 1. Product Context & Problem Statement

### Target Users
Commercial sales representatives, business development managers, and technical specification officers working in the paint, coatings, and commercial construction industries (e.g., Asian Paints, Berger, AkzoNobel, Kansai Nerolac).

### Problem
Sales teams spend up to 3 hours manually gathering firmographics, tender signals, architectural specifications, and paint volume requirements before customer meetings. Notes end up fragmented across personal notebooks, private Google Docs, and chat messages. When meetings conclude, follow-up actions and coating specifications are lost, resulting in zero institutional memory.

### Solution
MASCoT is a focused intelligence workspace where sales reps maintain permanent company intelligence briefs. 
- **Customer's Claude**: Performs external intelligence gathering, company research, and synthesis paid for by the customer's own Claude subscription.
- **MASCoT MCP Server**: Translates Claude tool calls to backend REST API operations over Streamable HTTP (`/mcp`).
- **MASCoT Application**: Provides the authoritative, persistent source of truth where records can be created, retrieved, filtered, edited, and exported with zero AI API costs.

---

## 2. Architecture Principle: Zero In-App AI

```
Customer's Claude ────(Streamable HTTP /mcp)────► MASCoT MCP Server
                                                        │
                                                        ▼ (REST API)
User Browser ──────────(React 18 / Vite)───────► MASCoT Backend API (FastAPI)
                                                        │
                                                        ▼ (SQLAlchemy ORM)
                                              Persistent Database (SQLite / Postgres)
```

- **NO OpenAI, Anthropic, or Gemini API keys in the app.**
- **NO embedded LLM or in-app chatbot.**
- **NO separate data stores**: Claude and the web application interact with the exact same database records in real time.

---

## 3. Technology Stack

- **Frontend**: React 18, Vite 6, Modern CSS (DM Sans & Manrope), Lucide React.
- **Backend**: Python 3.11+, FastAPI, SQLAlchemy 2.0 (Mapped Columns), Pydantic v2.
- **MCP Server**: Official Python `mcp` SDK (`mcp>=1.3.0,<2` FastMCP) using Streamable HTTP transport.
- **Database**: SQLite (local development) / PostgreSQL (production via Supabase or Render).
- **Deployment**: Vercel (Frontend), Render (FastAPI Backend & MCP Server), Render/Supabase (PostgreSQL).

---

## 4. Local Installation & Setup

### Prerequisites
- Python 3.11+
- Node.js 20+

### Clone & Repository Structure
```bash
mascot-workspace/
├── backend/            # FastAPI REST API & SQLAlchemy Models
├── frontend/           # React 18 + Vite Web Application
├── mcp_server/         # FastMCP Server (Streamable HTTP on /mcp)
├── tests/              # End-to-end acceptance test suite
├── ARCHITECTURE.md     # System architecture specification
├── API_DOCUMENTATION.md# Complete REST API reference
├── MCP_SETUP.md        # Claude MCP configuration guide
├── DEPLOYMENT.md       # Public deployment guide (Render + Vercel)
├── TEST_REPORT.md      # Verified QA test report
└── DEMO_SCRIPT.md      # 5-minute founder pitch and walkthrough script
```

### 1. Run the Backend API
```bash
cd backend
python -m pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app:app --reload --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive Swagger UI: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/health`

### 2. Run the MCP Server
In a separate terminal:
```bash
cd mcp_server
python -m pip install -r requirements.txt
cp .env.example .env
python server.py
```
- MCP Streamable HTTP Endpoint: `http://localhost:8001/mcp`

### 3. Run the Frontend Application
In a separate terminal:
```bash
cd frontend
npm install
npm run dev
```
- Open browser at `http://localhost:5173`

---

## 5. Connecting Claude via MCP

Add the following configuration to your `claude_desktop_config.json`:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "mascot-intelligence": {
      "url": "http://localhost:8001/mcp",
      "transport": "streamable-http"
    }
  }
}
```

### Try these sample prompts in Claude:
1. **Create Brief**:
   > *"Research ABC Infrastructure, a construction company based in Hyderabad. Prepare a company intelligence brief covering its business overview, potential paint requirements, relevant project signals, meeting preparation questions, and next steps. Include source URLs where available. Save the brief in MASCoT."*
2. **Retrieve Brief**:
   > *"Find the company intelligence brief for ABC Infrastructure in MASCoT and show me the information currently saved."*
3. **Update Brief**:
   > *"Update the ABC Infrastructure brief with these additional meeting notes: Validated demand for 45,000L epoxy protective coatings for Hyderabad Metro expansion. Set next step to submit primer batch for laboratory corrosion testing by Friday. Save the changes in MASCoT."*
4. **Verify Bidirectional Sync**:
   > *"Retrieve the latest ABC Infrastructure brief from MASCoT and show me its current next steps."*

---

## 6. Running Automated Tests

Run the backend REST API unit tests:
```bash
python backend/test_backend.py
```

Run the MCP tool integration tests:
```bash
python mcp_server/test_mcp.py
```

Execute the full 11-step end-to-end acceptance scenario:
```bash
python tests/test_e2e_acceptance.py
```
All test suites pass with a 100% success rate (see `TEST_REPORT.md`).

---

## 7. Public Deployment

Detailed deployment instructions for Render and Vercel are available in [DEPLOYMENT.md](DEPLOYMENT.md).

- **Backend**: Deploy `backend/` to Render Web Service (`uvicorn app:app --host 0.0.0.0 --port $PORT`).
- **MCP Server**: Deploy `mcp_server/` to Render Web Service (`python server.py`).
- **Frontend**: Deploy `frontend/` to Vercel (`npm run build`, output: `dist`). Set `VITE_API_URL`.
- **Database**: Use Render Managed PostgreSQL or Supabase.

---

## 8. Final Acceptance Criteria Verification

- [x] The frontend runs successfully without errors.
- [x] The backend runs successfully.
- [x] The database persists records across restarts.
- [x] Users can create company briefs.
- [x] Users can retrieve company briefs.
- [x] Users can edit company briefs.
- [x] Users can delete company briefs.
- [x] Users can search company briefs by company, industry, or location.
- [x] The MCP server starts successfully on Streamable HTTP (`/mcp`).
- [x] All four MCP tools (`create`, `get`, `list`, `update`) are available.
- [x] Claude can create a brief through MCP.
- [x] Claude can retrieve a brief through MCP.
- [x] Claude can update a brief through MCP.
- [x] Changes are synchronised bidirectionally between Claude and the web app.
- [x] Data survives browser refreshes and backend restarts.
- [x] Automated tests executed and reported in `TEST_REPORT.md`.
- [x] Public deployment configuration prepared (`render.yaml`, `vercel.json`, `DEPLOYMENT.md`).
- [x] Documentation and 5-minute pitch script complete (`DEMO_SCRIPT.md`).
- [x] **Zero AI models or AI API keys embedded in MASCoT.**
