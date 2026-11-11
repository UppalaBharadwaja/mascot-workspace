import asyncio
import os
import sys

# Ensure mcp_server and backend directories are in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
sys.path.insert(0, backend_dir)

from server import (
    create_company_brief,
    get_company_brief,
    list_company_briefs,
    update_company_brief,
    mcp
)

async def run_mcp_tests():
    print("=== STARTING MCP SERVER TOOL UNIT & INTEGRATION TESTS ===")

    # 0. Test tool discovery
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]
    print(f"Discovered MCP Tools: {tool_names}")
    expected_tools = ["create_company_brief", "get_company_brief", "list_company_briefs", "update_company_brief"]
    for expected in expected_tools:
        assert expected in tool_names, f"Tool '{expected}' not found in MCP server tools!"
    print("PASS: All 4 required MCP tools successfully registered and discoverable.")

    # 1. Test create_company_brief
    print("\n--- Testing Tool 1: create_company_brief ---")
    created_res = await create_company_brief(
        company_name="ABC Infrastructure",
        industry="Commercial Construction & Infrastructure",
        location="Hyderabad, Telangana",
        company_overview="Major regional EPC contractor specializing in highway overpasses, commercial IT parks, and metro stations.",
        potential_paint_requirements="High-performance epoxy floor coatings, anti-carbonation exterior wall paint, and intumescent fireproofing coatings.",
        project_signals="Awarded Phase 2 Hyderabad Metro extension; tender documents call for 45,000 liters of protective coating.",
        meeting_questions="What specifications are required for corrosion protection on exposed structural steelwork?",
        next_steps="Draft initial coating specification guide and submit to Chief Engineering Officer.",
        source_urls="https://abcinfra-demo.example.com\nhttps://tenderbulletin.example.com/2026/04"
    )

    assert created_res.get("success") is True, f"create_company_brief failed: {created_res}"
    assert "id" in created_res, "create_company_brief must return newly created record ID"
    assert "brief" in created_res, "create_company_brief must return saved company brief"
    brief_id = created_res["id"]
    saved_brief = created_res["brief"]
    assert saved_brief["company_name"] == "ABC Infrastructure"
    assert saved_brief["location"] == "Hyderabad, Telangana"
    print(f"PASS: create_company_brief created record ID {brief_id} with full payload.")

    # 2. Test get_company_brief
    print("\n--- Testing Tool 2: get_company_brief ---")
    get_res = await get_company_brief(brief_id=brief_id)
    assert get_res.get("id") == brief_id
    assert get_res.get("company_name") == "ABC Infrastructure"
    assert "potential_paint_requirements" in get_res
    print(f"PASS: get_company_brief successfully retrieved brief ID {brief_id}.")

    # Test get_company_brief with missing ID
    missing_res = await get_company_brief(brief_id=987654)
    assert missing_res.get("success") is False
    assert "Not Found" in missing_res.get("error", "")
    print("PASS: get_company_brief returns structured error for non-existent ID.")

    # 3. Test list_company_briefs
    print("\n--- Testing Tool 3: list_company_briefs ---")
    all_briefs = await list_company_briefs()
    assert isinstance(all_briefs, list)
    assert len(all_briefs) >= 1
    assert any(b["id"] == brief_id for b in all_briefs)
    print(f"PASS: list_company_briefs returned {len(all_briefs)} briefs.")

    # Search with matching query
    search_match = await list_company_briefs(search="Hyderabad")
    assert isinstance(search_match, list)
    assert any(b["id"] == brief_id for b in search_match)
    print("PASS: list_company_briefs successfully filtered by location keyword 'Hyderabad'.")

    # Search with non-matching query
    search_empty = await list_company_briefs(search="NonExistentCompany999")
    assert isinstance(search_empty, list)
    assert len(search_empty) == 0
    print("PASS: list_company_briefs returned empty list for non-matching query.")

    # 4. Test update_company_brief
    print("\n--- Testing Tool 4: update_company_brief ---")
    update_res = await update_company_brief(
        brief_id=brief_id,
        next_steps="Follow up with Procurement Director on Friday; provide sample batch for primer testing.",
        project_signals="Groundbreaking confirmed for Q3; coating volume revised to 60,000 liters."
    )
    assert update_res.get("success") is True, f"update_company_brief failed: {update_res}"
    assert "brief" in update_res
    updated_brief = update_res["brief"]
    assert "sample batch" in updated_brief["next_steps"]
    assert "60,000 liters" in updated_brief["project_signals"]
    assert updated_brief["company_name"] == "ABC Infrastructure"
    print(f"PASS: update_company_brief updated fields and preserved existing fields.")

    # Test update with non-existent ID
    update_missing = await update_company_brief(brief_id=987654, next_steps="test")
    assert update_missing.get("success") is False
    print("PASS: update_company_brief returned structured error for non-existent record.")

    print("\nALL MCP TOOL TESTS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_mcp_tests())
