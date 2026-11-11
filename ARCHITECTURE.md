# MASCoT – Company Intelligence Workspace
## System Architecture & Technical Specification

MASCoT (Market & Account Strategy Coordination Tool) is a specialised company intelligence workspace purpose-built for sales representatives and business development teams in the paint and commercial coatings industry. 

MASCoT implements the **"Zero In-App AI"** paradigm: **Claude does all the reasoning, research, analysis, and synthesis; MASCoT provides the persistent application, data storage, editing, retrieval, and synchronisation layer.**

---

## 1. High-Level Architecture Overview

```
┌────────────────────────────────────────────────────────┐
│                   Customer's Claude                    │
│   (Claude Desktop / Claude Web / Enterprise Connector) │
│       Does thinking, research, writing, reasoning      │
└───────────────────────────┬────────────────────────────┘
                            │
                            │ Model Context Protocol (MCP)
                            │ Streamable HTTP Transport (/mcp)
                            ▼
┌────────────────────────────────────────────────────────┐
│                   MASCoT MCP Server                    │
│                 (FastMCP / Python SDK)                 │
│         Translates Claude tool calls to REST APIs      │
└───────────────────────────┬────────────────────────────┘
                            │
                            │ REST API (JSON / HTTP)
                            ▼
┌────────────────────────────────────────────────────────┐
│                   MASCoT Backend                       │
│              (FastAPI / Python 3.11+)                  │
│       Business logic, validation, CRUD operations      │
└───────────────▲───────────────────────────┬────────────┘
                │                           │
                │ REST API                  │ SQLAlchemy ORM
                │ (JSON / HTTP)             ▼
┌───────────────┴────────────┐  ┌────────────────────────┐
│       MASCoT Frontend      │  │   Persistent Database   │
│     (React 18 + Vite)      │  │ SQLite (Local Dev)     │
│  Interactive SaaS Web App  │  │ PostgreSQL (Production)│
└────────────────────────────┘  └────────────────────────┘
```

---

## 2. Component Architecture

### A. Frontend Application (React + Vite)
- **Role**: User-facing web application for sales representatives.
- **Tech Stack**: React 18, Vite 6, Modern Vanilla CSS (DM Sans & Manrope typography), Lucide React icons.
- **Key Capabilities**:
  - Browse saved company briefs with real-time client-side and server-side filtering.
  - Create new company briefs with field validation.
  - View and edit all 11 brief attributes with auto-save timestamps.
  - Delete records with confirmation.
  - Interactive "Connect Claude via MCP" helper modal with copyable configurations.
  - Quick-copy sample Claude prompts to facilitate the external Claude workflow.
  - Responsive design adapting from desktop (3-column layout) to tablet and mobile.

### B. Backend Application (FastAPI + SQLAlchemy)
- **Role**: Authoritative data management and validation layer.
- **Tech Stack**: FastAPI, SQLAlchemy 2.0 (declarative mapped columns), Pydantic v2 schemas.
- **Key Capabilities**:
  - Clean RESTful endpoints conforming to standard HTTP semantics.
  - Pydantic validation for all incoming payloads.
  - Multi-dialect support: SQLite for instant local zero-config development; PostgreSQL (Supabase / Render) for production.
  - Automatic URL normalization (rewriting legacy `postgres://` to `postgresql://`).
  - CORS configuration enabling cross-origin requests from development and production frontend origins.
  - Swagger UI documentation available at `/docs` and OpenAPI JSON at `/openapi.json`.
  - Lightweight `/health` check endpoint for monitoring.

### C. MCP Server (Python MCP SDK / FastMCP)
- **Role**: Remote Model Context Protocol interface exposing MASCoT tools to Claude.
- **Tech Stack**: Official Python `mcp` SDK (FastMCP), HTTPX async client.
- **Transport**: Streamable HTTP transport listening on `http://localhost:8001/mcp` (or remote HTTPS).
- **Core Principle**: Stateless proxy. The MCP server does **not** maintain a secondary database or in-memory cache; it forwards all operations to the MASCoT backend REST API, ensuring complete data consistency between Claude and the web application.

---

## 3. Data Model & Database Schema

The core entity is the `CompanyBrief` model:

| Field Name | Type | Constraint | Description |
|---|---|---|---|
| `id` | Integer | Primary Key, Autoincrement | Unique identifier |
| `company_name` | String(180) | Not Null, Indexed | Name of the prospective company |
| `industry` | String(120) | Default: 'Paint / Construction' | Industry category |
| `location` | String(160) | Default: '' | City, State, Country |
| `company_overview` | Text | Default: '' | Core business, scale, operational context |
| `potential_paint_requirements` | Text | Default: '' | Protective coatings, decorative, industrial paint needs |
| `project_signals` | Text | Default: '' | Infrastructure projects, facility expansions, tenders |
| `meeting_questions` | Text | Default: '' | Strategic qualification & discovery questions |
| `next_steps` | Text | Default: '' | Action items, account owner follow-ups |
| `source_urls` | Text | Default: '' | Reference URLs and citations (one per line) |
| `created_at` | DateTime (UTC) | Default: current UTC time | Record creation timestamp |
| `updated_at` | DateTime (UTC) | Default: current UTC time | Timestamp of last modification |

---

## 4. API Specification

| Method | Endpoint | Description | Request Body | Response Code |
|---|---|---|---|---|
| `GET` | `/health` | Service health status | None | `200 OK` |
| `POST` | `/briefs` | Create a company brief | `BriefCreate` JSON | `201 Created` |
| `GET` | `/briefs` | List all briefs or search | Query: `?q={search_term}` | `200 OK` |
| `GET` | `/briefs/{id}` | Retrieve single brief | None | `200 OK` / `404 Not Found` |
| `PATCH` | `/briefs/{id}` | Update brief fields | `BriefUpdate` JSON | `200 OK` / `404 Not Found` |
| `DELETE` | `/briefs/{id}` | Delete brief | None | `204 No Content` / `404 Not Found` |

---

## 5. MCP Tool Specification

The MCP server exposes four operational tools to Claude:

### 1. `create_company_brief`
- **Description**: Save a new company intelligence brief in MASCoT.
- **Parameters**:
  - `company_name` (string, required)
  - `industry` (string, optional, default: `"Paint / Construction"`)
  - `location` (string, optional)
  - `company_overview` (string, optional)
  - `potential_paint_requirements` (string, optional)
  - `project_signals` (string, optional)
  - `meeting_questions` (string, optional)
  - `next_steps` (string, optional)
  - `source_urls` (string, optional)
- **Returns**: `{"success": true, "id": <int>, "brief": <BriefOut>}`

### 2. `get_company_brief`
- **Description**: Retrieve an individual company brief by its record ID.
- **Parameters**:
  - `brief_id` (integer, required)
- **Returns**: Complete brief JSON object or error status.

### 3. `list_company_briefs`
- **Description**: List saved briefs; optionally filter by search keyword.
- **Parameters**:
  - `search` (string, optional)
- **Returns**: Array of matching company briefs sorted by `updated_at DESC`.

### 4. `update_company_brief`
- **Description**: Update specific fields on an existing MASCoT company brief.
- **Parameters**:
  - `brief_id` (integer, required)
  - Optional update fields: `company_name`, `industry`, `location`, `company_overview`, `potential_paint_requirements`, `project_signals`, `meeting_questions`, `next_steps`, `source_urls`.
- **Returns**: `{"success": true, "id": <int>, "brief": <BriefOut>}`

---

## 6. Data Synchronization Mechanism

1. **Unified Storage**: Both human sales reps using the React app and external Claude clients communicate with the same FastAPI backend instance.
2. **Atomic Updates**: All updates trigger a fresh `updated_at` timestamp in UTC.
3. **Optimistic Retrieval**: When Claude updates a brief, the next web app refresh or query fetches the latest database state. Similarly, when a human edits next steps in the web UI, Claude's subsequent `get_company_brief` or `list_company_briefs` tool call immediately receives the updated values.

---

## 7. Public Deployment Strategy

- **Frontend**: Hosted on **Vercel** with global CDN distribution. Configured with environment variable `VITE_API_URL` pointing to the public backend.
- **Backend API**: Hosted on **Render** (Web Service). Configured with `DATABASE_URL` and `CORS_ORIGINS`.
- **MCP Server**: Hosted on **Render** (Web Service) using Streamable HTTP transport on `/mcp`. Configured with `BACKEND_URL` and `PORT`.
- **Database**: **Supabase** or **Render Managed PostgreSQL** for persistent relational storage in production.
