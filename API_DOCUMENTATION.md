# MASCoT API Documentation
## REST API Reference for MASCoT – Company Intelligence Workspace

The MASCoT backend is a RESTful service built with FastAPI, SQLAlchemy 2.0, and Pydantic v2. It acts as the single source of truth for all company intelligence briefs, serving both the React frontend and the external Claude MCP server.

Interactive Swagger UI documentation is available at `/docs` and OpenAPI schema at `/openapi.json`.

---

## Base URLs
- **Local Development**: `http://localhost:8000`
- **Render Production**: `https://<YOUR-RENDER-API-URL>.onrender.com`

---

## Data Schema: CompanyBrief

```json
{
  "id": 1,
  "company_name": "ABC Infrastructure",
  "industry": "Infrastructure & Commercial EPC",
  "location": "Hyderabad, Telangana",
  "company_overview": "Top-tier regional EPC contractor handling highway overpasses...",
  "potential_paint_requirements": "High-build epoxy floor coatings, anti-carbonation paints...",
  "project_signals": "Awarded Phase 2 Hyderabad Metro extension tender...",
  "meeting_questions": "What are your required DFT specifications for coastal bridge sections?",
  "next_steps": "Submit preliminary coating schedule to VP Engineering by Friday.",
  "source_urls": "https://abcinfra-demo.example.com\nhttps://tenderbulletin.example.com",
  "created_at": "2026-11-11T13:30:00Z",
  "updated_at": "2026-11-11T13:36:21Z"
}
```

---

## Endpoints

### 1. Health Check
`GET /health`

Verifies that the backend API is live and can communicate with the persistent database.

**Response (200 OK):**
```json
{
  "status": "ok",
  "service": "mascot-api",
  "database": "connected"
}
```

---

### 2. Create Company Brief
`POST /briefs`

Creates and permanently saves a new company intelligence brief.

**Request Headers:** `Content-Type: application/json`

**Request Body (`BriefCreate`):**
```json
{
  "company_name": "ABC Infrastructure",
  "industry": "Infrastructure & Commercial EPC",
  "location": "Hyderabad, Telangana",
  "company_overview": "Top-tier regional EPC contractor handling highway overpasses...",
  "potential_paint_requirements": "High-build epoxy floor coatings, anti-carbonation facade paints...",
  "project_signals": "Awarded Phase 2 Hyderabad Metro extension tender...",
  "meeting_questions": "What are your required DFT specifications for coastal bridge sections?",
  "next_steps": "Submit preliminary coating schedule to VP Engineering by Friday.",
  "source_urls": "https://abcinfra-demo.example.com"
}
```

**Response (201 Created):**
Returns the complete created `CompanyBrief` object with assigned `id`, `created_at`, and `updated_at`.

**Error Responses:**
- `422 Unprocessable Entity`: Missing or blank `company_name`.

---

### 3. List / Search Company Briefs
`GET /briefs`
`GET /briefs?q={search_term}`

Retrieves saved briefs ordered by `updated_at DESC`. When the optional query parameter `q` is provided, performs case-insensitive matching across `company_name`, `industry`, and `location`.

**Query Parameters:**
- `q` (string, optional): Search keyword.

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "company_name": "ABC Infrastructure",
    "industry": "Infrastructure & Commercial EPC",
    "location": "Hyderabad, Telangana",
    "company_overview": "...",
    "potential_paint_requirements": "...",
    "project_signals": "...",
    "meeting_questions": "...",
    "next_steps": "...",
    "source_urls": "...",
    "created_at": "2026-11-11T13:30:00Z",
    "updated_at": "2026-11-11T13:36:21Z"
  }
]
```

---

### 4. Get Individual Brief
`GET /briefs/{brief_id}`

Retrieves an individual brief by its integer primary key.

**Path Parameters:**
- `brief_id` (integer, required)

**Response (200 OK):**
Returns single `CompanyBrief` object.

**Error Responses:**
- `404 Not Found`:
```json
{
  "detail": "Company brief with ID 999 not found"
}
```

---

### 5. Update Company Brief
`PATCH /briefs/{brief_id}`

Updates one or more fields on an existing brief. Automatically refreshes `updated_at` to the current UTC timestamp.

**Path Parameters:**
- `brief_id` (integer, required)

**Request Body (`BriefUpdate`):**
Any subset of fields can be provided:
```json
{
  "next_steps": "Action 1: Dispatch 20L primer sample for testing by Thursday.",
  "project_signals": "Confirmed expansion into Phase 2 metro line."
}
```

**Response (200 OK):**
Returns the updated `CompanyBrief` object.

**Error Responses:**
- `404 Not Found`: If record does not exist.
- `422 Unprocessable Entity`: If `company_name` is explicitly set to empty whitespace.

---

### 6. Delete Company Brief
`DELETE /briefs/{brief_id}`

Permanently removes a company brief from the persistent database.

**Path Parameters:**
- `brief_id` (integer, required)

**Response (204 No Content):**
Empty response body.

**Error Responses:**
- `404 Not Found`: If record does not exist or has already been deleted.
