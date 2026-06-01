import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def get_listing_with_valuation():
    """Helper — returns a listing ID that has a valuation."""
    r = client.get("/api/v1/listings?limit=1")
    items = r.json()["data"]
    for item in items:
        if item.get("valuation"):
            return item["id"]
    return items[0]["id"] if items else None


class TestValuationsEndpoint:

    def test_returns_200_for_valid_listing(self):
        listing_id = get_listing_with_valuation()
        assert listing_id is not None
        r = client.get(f"/api/v1/valuations/{listing_id}")
        assert r.status_code == 200

    def test_returns_404_for_missing(self):
        r = client.get("/api/v1/valuations/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 404

    def test_response_has_estimated_value(self):
        listing_id = get_listing_with_valuation()
        r = client.get(f"/api/v1/valuations/{listing_id}")
        data = r.json()
        assert "estimated_value" in data
        assert data["estimated_value"] is not None
        assert float(data["estimated_value"]) > 0

    def test_response_has_confidence(self):
        listing_id = get_listing_with_valuation()
        r = client.get(f"/api/v1/valuations/{listing_id}")
        data = r.json()
        assert "confidence" in data
        confidence = float(data["confidence"])
        assert 0.0 <= confidence <= 1.0

    def test_response_has_method(self):
        listing_id = get_listing_with_valuation()
        r = client.get(f"/api/v1/valuations/{listing_id}")
        data = r.json()
        assert data["method"] == "ridge_regression"

    def test_response_has_comp_count(self):
        listing_id = get_listing_with_valuation()
        r = client.get(f"/api/v1/valuations/{listing_id}")
        data = r.json()
        assert "comp_count" in data
        assert data["comp_count"] > 0

    def test_listing_id_matches(self):
        listing_id = get_listing_with_valuation()
        r = client.get(f"/api/v1/valuations/{listing_id}")
        data = r.json()
        assert data["listing_id"] == listing_id