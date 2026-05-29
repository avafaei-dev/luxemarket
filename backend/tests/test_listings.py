import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


class TestListingsEndpoint:

    def test_returns_200(self):
        r = client.get("/api/v1/listings")
        assert r.status_code == 200

    def test_response_shape(self):
        r = client.get("/api/v1/listings?limit=5")
        data = r.json()
        assert "data" in data
        assert "total" in data
        assert "page" in data
        assert "limit" in data

    def test_pagination(self):
        r1 = client.get("/api/v1/listings?page=1&limit=10")
        r2 = client.get("/api/v1/listings?page=2&limit=10")
        ids1 = {item["id"] for item in r1.json()["data"]}
        ids2 = {item["id"] for item in r2.json()["data"]}
        # Pages should not overlap
        assert ids1.isdisjoint(ids2)

    def test_filter_by_make(self):
        r = client.get("/api/v1/listings?make=BMW&limit=50")
        data = r.json()
        assert data["total"] > 0
        for item in data["data"]:
            assert item["make"] == "BMW"

    def test_filter_by_price_range(self):
        r = client.get("/api/v1/listings?price_min=50000&price_max=100000&limit=50")
        data = r.json()
        for item in data["data"]:
            assert 50000 <= float(item["price"]) <= 100000

    def test_filter_by_condition(self):
        r = client.get("/api/v1/listings?condition=used&limit=20")
        data = r.json()
        for item in data["data"]:
            assert item["condition"] == "used"

    def test_invalid_condition_rejected(self):
        r = client.get("/api/v1/listings?condition=junk")
        assert r.status_code == 422

    def test_sort_price_asc(self):
        r = client.get("/api/v1/listings?sort=price_asc&limit=20")
        prices = [float(item["price"]) for item in r.json()["data"]]
        assert prices == sorted(prices)

    def test_sort_price_desc(self):
        r = client.get("/api/v1/listings?sort=price_desc&limit=20")
        prices = [float(item["price"]) for item in r.json()["data"]]
        assert prices == sorted(prices, reverse=True)

    def test_limit_respected(self):
        r = client.get("/api/v1/listings?limit=7")
        assert len(r.json()["data"]) == 7

    def test_total_matches_db(self):
        r = client.get("/api/v1/listings")
        assert r.json()["total"] > 0


class TestListingDetail:

    def _get_first_id(self):
        r = client.get("/api/v1/listings?limit=1")
        return r.json()["data"][0]["id"]

    def test_returns_200_for_valid_id(self):
        listing_id = self._get_first_id()
        r = client.get(f"/api/v1/listings/{listing_id}")
        assert r.status_code == 200

    def test_returns_404_for_missing(self):
        r = client.get("/api/v1/listings/00000000-0000-0000-0000-000000000000")
        assert r.status_code == 404

    def test_detail_has_all_fields(self):
        listing_id = self._get_first_id()
        r = client.get(f"/api/v1/listings/{listing_id}")
        data = r.json()
        for field in ["id", "make", "model", "year", "price", "condition", "mileage"]:
            assert field in data


class TestMakesEndpoint:

    def test_returns_200(self):
        r = client.get("/api/v1/makes")
        assert r.status_code == 200

    def test_returns_all_makes(self):
        r = client.get("/api/v1/makes")
        makes = {item["make"] for item in r.json()}
        assert "BMW" in makes
        assert "Porsche" in makes
        assert "Ferrari" in makes

    def test_count_is_positive(self):
        r = client.get("/api/v1/makes")
        for item in r.json():
            assert item["count"] > 0

    def test_models_for_make(self):
        r = client.get("/api/v1/makes/BMW/models")
        assert r.status_code == 200
        assert len(r.json()) > 0

    def test_models_for_unknown_make_returns_empty(self):
        r = client.get("/api/v1/makes/NotABrand/models")
        assert r.status_code == 200
        assert r.json() == []


class TestTopDeals:

    def test_returns_200(self):
        r = client.get("/api/v1/listings/top-deals")
        assert r.status_code == 200

    def test_response_shape(self):
        r = client.get("/api/v1/listings/top-deals")
        data = r.json()
        assert "data" in data
        assert "total" in data


class TestTrends:

    def test_summary_returns_200(self):
        r = client.get("/api/v1/trends/summary")
        assert r.status_code == 200

    def test_summary_has_listing_count(self):
        r = client.get("/api/v1/trends/summary")
        data = r.json()
        assert "total_listings" in data
        assert data["total_listings"] > 0