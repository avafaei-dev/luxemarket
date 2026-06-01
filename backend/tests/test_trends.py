import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestTrendsEndpoint:

    def test_returns_200(self):
        r = client.get("/api/v1/trends")
        assert r.status_code == 200

    def test_response_shape(self):
        r = client.get("/api/v1/trends")
        data = r.json()
        assert "data" in data
        assert "total" in data

    def test_returns_all_snapshots(self):
        r = client.get("/api/v1/trends")
        assert r.json()["total"] > 0

    def test_snapshot_has_required_fields(self):
        r = client.get("/api/v1/trends")
        item = r.json()["data"][0]
        for field in ["make", "model", "avg_price", "listing_count", "avg_deal_score"]:
            assert field in item

    def test_filter_by_make(self):
        r = client.get("/api/v1/trends?make=Porsche")
        data = r.json()
        assert data["total"] > 0
        for item in data["data"]:
            assert item["make"] == "Porsche"

    def test_filter_by_make_and_model(self):
        r = client.get("/api/v1/trends?make=BMW&model=M3 Competition")
        data = r.json()
        assert data["total"] >= 1
        assert data["data"][0]["make"] == "BMW"

    def test_unknown_make_returns_empty(self):
        r = client.get("/api/v1/trends?make=NotABrand")
        assert r.json()["total"] == 0

    def test_avg_price_is_positive(self):
        r = client.get("/api/v1/trends")
        for item in r.json()["data"]:
            if item["avg_price"] is not None:
                assert item["avg_price"] > 0

    def test_summary_returns_200(self):
        r = client.get("/api/v1/trends/summary")
        assert r.status_code == 200

    def test_summary_has_all_fields(self):
        r = client.get("/api/v1/trends/summary")
        data = r.json()
        for field in ["total_listings", "avg_price", "avg_deal_score", "top_make"]:
            assert field in data

    def test_summary_listing_count_positive(self):
        r = client.get("/api/v1/trends/summary")
        assert r.json()["total_listings"] > 0

    def test_summary_avg_price_positive(self):
        r = client.get("/api/v1/trends/summary")
        assert r.json()["avg_price"] > 0

    def test_summary_top_make_is_string(self):
        r = client.get("/api/v1/trends/summary")
        assert isinstance(r.json()["top_make"], str)