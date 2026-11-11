import asyncio
import os
import sys
import httpx
from datetime import datetime

# Path setup
workspace_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(workspace_dir, "mcp_server"))
sys.path.insert(0, os.path.join(workspace_dir, "backend"))

from server import (
    create_company_brief,
    get_company_brief,
    list_company_briefs,
    update_company_brief
)

BACKEND_API = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")

async def run_e2e_acceptance():
    print("=" * 70)
    print("MASCoT END-TO-END ACCEPTANCE TEST SUITE")
    print("Zero In-App AI · MCP External Intelligence · Bidirectional Synchronisation")
    print("=" * 70)

    results = []

    async with httpx.AsyncClient(timeout=15.0) as client:
        # STEP 1: Verify clean database state (clean up any test ABC Infrastructure records)
        print("\n[Step 1] Starting with clean database state...")
        list_res = await client.get(f"{BACKEND_API}/briefs")
        assert list_res.status_code == 200, f"Backend unreachable: {list_res.text}"
        existing = list_res.json()
        for item in existing:
            if "ABC Infrastructure" in item.get("company_name", ""):
                del_res = await client.delete(f"{BACKEND_API}/briefs/{item['id']}")
                assert del_res.status_code == 204
        
        # Verify no ABC Infrastructure exists
        verify_clean = await client.get(f"{BACKEND_API}/briefs?q=ABC%20Infrastructure")
        assert len(verify_clean.json()) == 0
        print("  [OK] Step 1 PASSED: Database state verified and clean of test records.")
        results.append(("Step 1: Start with clean database", True))

        # STEP 2 & 3: Ask Claude to create brief for ABC Infrastructure via MCP
        print("\n[Step 2 & 3] Claude calls MCP tool: create_company_brief...")
        mcp_payload = {
            "company_name": "ABC Infrastructure",
            "industry": "Infrastructure & Commercial EPC",
            "location": "Hyderabad, Telangana",
            "company_overview": "Top-tier regional EPC contractor handling highway overpasses, commercial IT parks, and metro rail projects across South India.",
            "potential_paint_requirements": "High-build epoxy floor coatings for warehouses, anti-carbonation facade paints, and intumescent structural steel fireproofing.",
            "project_signals": "Awarded Phase 2 Hyderabad Metro extension tender; estimated requirement of 45,000L protective coatings.",
            "meeting_questions": "What are your required DFT (dry film thickness) specifications for coastal bridge sections? Who signs off on vendor approvals?",
            "next_steps": "Submit preliminary coating schedule to VP Engineering by Friday.",
            "source_urls": "https://abcinfrastructure-demo.com\nhttps://tenderbulletin.example.com/hyderabad-metro"
        }
        
        mcp_create_res = await create_company_brief(**mcp_payload)
        assert mcp_create_res.get("success") is True, f"MCP creation failed: {mcp_create_res}"
        created_id = mcp_create_res["id"]
        saved_brief = mcp_create_res["brief"]
        assert saved_brief["company_name"] == "ABC Infrastructure"
        assert saved_brief["id"] == created_id
        print(f"  [OK] Step 2 & 3 PASSED: MCP created brief ID {created_id} with full intelligence payload.")
        results.append(("Step 2 & 3: Claude creates brief via MCP", True))

        # STEP 4 & 5: Open MASCoT web application and confirm record appears
        print("\n[Step 4 & 5] Web application queries backend: GET /briefs...")
        web_list_res = await client.get(f"{BACKEND_API}/briefs")
        assert web_list_res.status_code == 200
        all_briefs = web_list_res.json()
        target = next((b for b in all_briefs if b["id"] == created_id), None)
        assert target is not None, f"Record ID {created_id} did not appear in web app list!"
        assert target["company_name"] == "ABC Infrastructure"
        assert target["location"] == "Hyderabad, Telangana"
        assert target["potential_paint_requirements"] == mcp_payload["potential_paint_requirements"]
        print(f"  [OK] Step 4 & 5 PASSED: Web app retrieves record ID {created_id} matching Claude's MCP submission.")
        results.append(("Step 4 & 5: Record appears in MASCoT web application", True))

        # STEP 6 & 7: User edits 'next_steps' in web application and saves
        print("\n[Step 6 & 7] User edits 'next_steps' in web application: PATCH /briefs/{id}...")
        updated_next_steps = (
            "MEETING HELD 11-NOV: Agreed on 45,000L epoxy requirement. "
            "Action 1: Dispatch 20L primer sample for laboratory corrosion testing by Thursday. "
            "Action 2: Send commercial quote to Head of Procurement by next Monday."
        )
        web_edit_res = await client.patch(
            f"{BACKEND_API}/briefs/{created_id}",
            json={"next_steps": updated_next_steps}
        )
        assert web_edit_res.status_code == 200, f"Web app PATCH failed: {web_edit_res.text}"
        edited_brief = web_edit_res.json()
        assert edited_brief["next_steps"] == updated_next_steps
        assert edited_brief["company_name"] == "ABC Infrastructure" # Preserved
        print(f"  [OK] Step 6 & 7 PASSED: Web app saved updated next steps successfully.")
        results.append(("Step 6 & 7: Edit and save next steps in web application", True))

        # STEP 8 & 9: Ask Claude to retrieve the updated brief via MCP
        print("\n[Step 8 & 9] Claude retrieves brief via MCP: get_company_brief...")
        claude_retrieved = await get_company_brief(brief_id=created_id)
        assert claude_retrieved.get("id") == created_id
        assert claude_retrieved.get("next_steps") == updated_next_steps
        print(f"  [OK] Step 8 & 9 PASSED: Claude retrieved updated brief via MCP; next_steps matches UI edit perfectly!")
        results.append(("Step 8 & 9: Claude retrieves updated brief via MCP", True))

        # STEP 10 & 11: Refresh web application and confirm changes remain saved
        print("\n[Step 10 & 11] Refresh web application: GET /briefs/{id} from database...")
        refresh_res = await client.get(f"{BACKEND_API}/briefs/{created_id}")
        assert refresh_res.status_code == 200
        refreshed_data = refresh_res.json()
        assert refreshed_data["next_steps"] == updated_next_steps
        assert refreshed_data["company_name"] == "ABC Infrastructure"
        assert refreshed_data["updated_at"] is not None
        print("  [OK] Step 10 & 11 PASSED: Data survived refresh and persists permanently in storage.")
        results.append(("Step 10 & 11: Refresh web app & verify persistence", True))

    print("\n" + "=" * 70)
    print("END-TO-END ACCEPTANCE TEST SUMMARY:")
    for name, passed in results:
        status = "PASSED" if passed else "FAILED"
        print(f"  [{status}] {name}")
    print("=" * 70)
    print("ALL 11 ACCEPTANCE SCENARIO STEPS EXECUTED AND PASSED WITH ZERO ERRORS.\n")
    return True

if __name__ == "__main__":
    success = asyncio.run(run_e2e_acceptance())
    sys.exit(0 if success else 1)
