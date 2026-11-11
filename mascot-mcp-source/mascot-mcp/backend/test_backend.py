import os
import sys

# Ensure backend directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app import app
from database import Base, engine

Base.metadata.create_all(bind=engine)
client = TestClient(app)

def run_all_tests():
    print("=== STARTING BACKEND REST API TESTS ===")
    
    # 1. Health check
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    assert res.json()["status"] == "ok"
    print("PASS: /health endpoint")

    # 2. Create brief (valid)
    payload = {
        "company_name": "Asian Paints Limited",
        "industry": "Paint / Coatings Manufacturing",
        "location": "Mumbai, Maharashtra",
        "company_overview": "India's largest paint company and manufacturer of decorative and industrial coatings.",
        "potential_paint_requirements": "High demand for protective architectural coatings, waterproofing solutions, and industrial enamel.",
        "project_signals": "Expanding production facilities in South India; newly announced smart factory initiative.",
        "meeting_questions": "What are your current procurement lead times for specialized raw polymer resins?",
        "next_steps": "Schedule discovery call with VP of Procurement next Tuesday.",
        "source_urls": "https://www.asianpaints.com\nhttps://economictimes.indiatimes.com"
    }
    res = client.post("/briefs", json=payload)
    assert res.status_code == 201, f"Create brief failed: {res.text}"
    created = res.json()
    brief_id = created["id"]
    assert created["company_name"] == payload["company_name"]
    assert created["industry"] == payload["industry"]
    assert created["location"] == payload["location"]
    assert "created_at" in created
    assert "updated_at" in created
    print(f"PASS: POST /briefs - Created brief with ID {brief_id}")

    # 3. Create brief (invalid - blank company_name)
    bad_payload = {"company_name": "   ", "industry": "Paint"}
    res = client.post("/briefs", json=bad_payload)
    assert res.status_code == 422, f"Expected 422 for blank name, got {res.status_code}"
    print("PASS: POST /briefs - Validation rejected blank company_name (422)")

    # 4. Get brief by ID
    res = client.get(f"/briefs/{brief_id}")
    assert res.status_code == 200, f"Get brief failed: {res.text}"
    fetched = res.json()
    assert fetched["id"] == brief_id
    assert fetched["company_name"] == "Asian Paints Limited"
    print(f"PASS: GET /briefs/{brief_id} - Successfully retrieved record")

    # 5. Get non-existent brief (404)
    res = client.get("/briefs/999999")
    assert res.status_code == 404, f"Expected 404 for missing brief, got {res.status_code}"
    print("PASS: GET /briefs/999999 - Missing record returns 404")

    # 6. List briefs (unfiltered)
    res = client.get("/briefs")
    assert res.status_code == 200
    briefs = res.json()
    assert len(briefs) >= 1
    assert any(b["id"] == brief_id for b in briefs)
    print(f"PASS: GET /briefs - Retrieved {len(briefs)} records")

    # 7. Search briefs by query
    res = client.get("/briefs?q=Mumbai")
    assert res.status_code == 200
    search_results = res.json()
    assert len(search_results) >= 1
    assert any(b["id"] == brief_id for b in search_results)
    print(f"PASS: GET /briefs?q=Mumbai - Found matching record by location")

    res = client.get("/briefs?q=NonExistentKeywordXYZ")
    assert res.status_code == 200
    assert len(res.json()) == 0
    print("PASS: GET /briefs?q=NonExistentKeywordXYZ - Returns empty list for unmatched query")

    # 8. Update brief (PATCH)
    update_payload = {
        "next_steps": "Follow up completed. Proposal sent to head of commercial sales."
    }
    res = client.patch(f"/briefs/{brief_id}", json=update_payload)
    assert res.status_code == 200, f"Update brief failed: {res.text}"
    updated = res.json()
    assert updated["next_steps"] == update_payload["next_steps"]
    assert updated["company_name"] == "Asian Paints Limited"  # Other fields preserved
    print("PASS: PATCH /briefs/{id} - Successfully updated field")

    # 9. Update non-existent brief (404)
    res = client.patch("/briefs/999999", json={"next_steps": "new"})
    assert res.status_code == 404
    print("PASS: PATCH /briefs/999999 - Returns 404 for missing record")

    # 10. Delete brief
    res = client.delete(f"/briefs/{brief_id}")
    assert res.status_code == 204, f"Delete brief failed: {res.status_code}"
    print(f"PASS: DELETE /briefs/{brief_id} - Record deleted (204)")

    # 11. Confirm record is deleted
    res = client.get(f"/briefs/{brief_id}")
    assert res.status_code == 404
    print("PASS: GET /briefs/{id} after DELETE returns 404")

    # 12. Delete non-existent brief (404)
    res = client.delete(f"/briefs/{brief_id}")
    assert res.status_code == 404
    print("PASS: DELETE /briefs/{id} on already deleted record returns 404")

    print("\nALL 12 BACKEND UNIT AND INTEGRATION TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_all_tests()
