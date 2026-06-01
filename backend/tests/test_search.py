import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def post_search(payload: dict):
    return client.post(
        "/api/v1/listings/search",
        json=payload,
        headers={"Content-Type": "application/json"},
    )


class TestSearchEndpoint:

    def test_returns_200(self):
        r = post_search({})
        assert r.status_code == 200

    def test_response_shape(self):
        r = post_search({})
        data = r.json()
        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data

    def test_empty_body_returns_all(self):
        r = post_search({})
        assert r.json()["total"] > 0

    def test_free_text_query_make(self):
        r = post_search({"query": "BMW"})
        data = r.json()
        assert data["total"] > 0
        for item in data["data"]:
            # Query matches against make, model, description — BMW should appear in make
            text = f"{item['make']} {item['model']}".lower()
            assert "bmw" in text

    def test_multi_make_filter(self):
        r = post_search({"make": ["BMW", "Porsche"]})
        data = r.json()
        assert data["total"] > 0
        for item in data["data"]:
            assert item["make"] in ["BMW", "Porsche"]

    def test_single_make_filter(self):
        r = post_search({"make": ["Ferrari"]})
        data = r.json()
        for item in data["data"]:
            assert item["make"] == "Ferrari"

    def test_price_range_filter(self):
        r = post_search({"price_min": 50000, "price_max": 100000})
        data = r.json()
        for item in data["data"]:
            assert 50000 <= float(item["price"]) <= 100000

    def test_condition_filter(self):
        r = post_search({"condition": ["new"]})
        data = r.json()
        for item in data["data"]:
            assert item["condition"] == "new"

    def test_multi_condition_filter(self):
        r = post_search({"condition": ["new", "cpo"]})
        data = r.json()
        for item in data["data"]:
            assert item["condition"] in ["new", "cpo"]

    def test_year_range_filter(self):
        r = post_search({"year_min": 2020, "year_max": 2022})
        data = r.json()
        for item in data["data"]:
            assert 2020 <= item["year"] <= 2022

    def test_mileage_max_filter(self):
        r = post_search({"mileage_max": 20000})
        data = r.json()
        for item in data["data"]:
            if item["mileage"] is not None:
                assert item["mileage"] <= 20000

    def test_min_deal_score_filter(self):
        r = post_search({"min_deal_score": 70})
        data = r.json()
        for item in data["data"]:
            if item["deal_score"]:
                assert float(item["deal_score"]["score"]) >= 70

    def test_sort_price_asc(self):
        r = post_search({"sort": "price_asc", "limit": 20})
        prices = [float(item["price"]) for item in r.json()["data"]]
        assert prices == sorted(prices)

    def test_sort_price_desc(self):
        r = post_search({"sort": "price_desc", "limit": 20})
        prices = [float(item["price"]) for item in r.json()["data"]]
        assert prices == sorted(prices, reverse=True)

    def test_pagination(self):
        r1 = post_search({"page": 1, "limit": 5, "sort": "price_asc"})
        r2 = post_search({"page": 2, "limit": 5, "sort": "price_asc"})
        ids1 = {item["id"] for item in r1.json()["data"]}
        ids2 = {item["id"] for item in r2.json()["data"]}
        assert ids1.isdisjoint(ids2)

    def test_combined_filters(self):
        r = post_search({
            "make": ["BMW", "Audi"],
            "price_max": 90000,
            "condition": ["used"],
            "sort": "price_asc",
        })
        data = r.json()
        for item in data["data"]:
            assert item["make"] in ["BMW", "Audi"]
            assert float(item["price"]) <= 90000
            assert item["condition"] == "used"

    def test_no_results_returns_empty_list(self):
        r = post_search({"price_min": 99999999})
        data = r.json()
        assert data["total"] == 0
        assert data["data"] == []

    def test_location_state_filter(self):
        r = post_search({"location_state": ["CA"]})
        data = r.json()
        assert data["total"] > 0
        for item in data["data"]:
            assert item["location_state"] == "CA"