import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_returns_200():
    response = client.get("/api/v1/health")
    assert response.status_code == 200


def test_health_response_shape():
    response = client.get("/api/v1/health")
    data = response.json()
    assert "status" in data
    assert "db" in data
    assert data["status"] == "ok"


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "LuxeMarket" in response.json()["name"]