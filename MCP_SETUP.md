# MASCoT – MCP Integration & Setup Guide
## Connecting Claude to MASCoT via Model Context Protocol (MCP)

This document provides complete instructions for connecting a customer's external Claude account (Claude Desktop, Claude Web, or Claude for Teams/Enterprise) to the MASCoT workspace via the official Model Context Protocol (MCP).

---

## Architecture Principle: Zero In-App AI

MASCoT does not contain an internal AI model or embedded API keys. 
- **Customer's Claude**: Performs web research, competitive analysis, qualification reasoning, and copywriting.
- **MASCoT MCP Server**: Receives standard tool calls from Claude and translates them to REST API operations against MASCoT's persistent database.
- **MASCoT Frontend**: Lets sales reps view, filter, edit, and export the records that Claude creates or updates.

---

## 1. Connecting to Claude Desktop

### A. Prerequisites
- Claude Desktop installed (macOS or Windows).
- MASCoT MCP server running locally or deployed publicly.

### B. Configuration File Location
Open or create your Claude Desktop configuration file:
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

### C. Configuration Snippet (Streamable HTTP / Remote)

#### For Local Development:
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

#### For Production Deployed Service (Render):
```json
{
  "mcpServers": {
    "mascot-intelligence": {
      "url": "https://mascot-mcp.onrender.com/mcp",
      "transport": "streamable-http"
    }
  }
}
```

### D. Verifying the Connection
1. Launch or restart Claude Desktop.
2. In the bottom-right corner of the Claude prompt box, click the **Hammer / Tools** icon.
3. Verify that the 4 MASCoT tools are visible:
   - `create_company_brief`
   - `get_company_brief`
   - `list_company_briefs`
   - `update_company_brief`

---

## 2. Connecting to Claude Enterprise / Remote MCP Connectors

If using Claude Web with Custom MCP Connectors:
1. Navigate to **Claude Settings > Integrations / MCP Connectors**.
2. Click **Add Remote MCP Connector**.
3. Enter the public endpoint: `https://<YOUR-RENDER-MCP-URL>.onrender.com/mcp`.
4. Select **Streamable HTTP** as the transport type.
5. Save the integration. When starting a new conversation in Claude, ensure the MASCoT workspace connector is checked.

---

## 3. The Four MASCoT Operational Tools

| Tool Name | Purpose | Key Inputs | Output |
|---|---|---|---|
| `create_company_brief` | Create & save new brief | `company_name`, `industry`, `location`, `company_overview`, `potential_paint_requirements`, `project_signals`, `meeting_questions`, `next_steps`, `source_urls` | Success status, ID, saved brief |
| `get_company_brief` | Retrieve single brief | `brief_id` (integer) | Complete brief object |
| `list_company_briefs` | List & filter briefs | `search` (optional string) | Array of matching briefs |
| `update_company_brief` | Update existing fields | `brief_id` (integer), plus any fields to change | Success status, ID, updated brief |

---

## 4. Sample Prompts and Test Scenarios

### Prompt 1: Research and Create Brief
> **User Prompt:**  
> "Research ABC Infrastructure, a construction company based in Hyderabad. Prepare a company intelligence brief covering its business overview, potential paint requirements, relevant project signals, meeting preparation questions, and next steps. Include source URLs where available. Save the brief in MASCoT."

**Expected Behaviour:**  
Claude searches the web and synthesizes findings into the structured fields of the paint & coatings domain, then calls `create_company_brief`. The new record immediately appears in MASCoT's web interface.

---

### Prompt 2: Retrieve a Saved Brief
> **User Prompt:**  
> "Find the company intelligence brief for ABC Infrastructure in MASCoT and show me the information currently saved."

**Expected Behaviour:**  
Claude invokes `list_company_briefs(search="ABC Infrastructure")` or `get_company_brief`, parses the returned record, and displays the saved intelligence to the user.

---

### Prompt 3: Update an Existing Brief
> **User Prompt:**  
> "Update the ABC Infrastructure brief with these additional meeting notes: Validated demand for 45,000L epoxy protective coatings for Hyderabad Metro expansion. Set next step to submit primer batch for laboratory corrosion testing by Friday. Save the changes in MASCoT."

**Expected Behaviour:**  
Claude finds the matching record ID and invokes `update_company_brief(brief_id=..., next_steps="...", project_signals="...")`. MASCoT updates the record, increments the `updated_at` timestamp, and preserves all other fields.

---

### Prompt 4: Verify Bidirectional Synchronisation
> **User Prompt:**  
> "Retrieve the latest ABC Infrastructure brief from MASCoT and show me its current next steps."

**Expected Behaviour:**  
Claude calls `get_company_brief` and presents the latest data—including any manual edits made directly in the MASCoT web app by a sales rep.
