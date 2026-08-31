"""
Tests for the /health endpoint.

Key concepts demonstrated:
    - Using FastAPI's TestClient to simulate HTTP requests without
      starting a real server
    - Writing assertions to verify response status codes and body content
    - Pytest automatically discovers functions that start with "test_"
"""

from fastapi.testclient import TestClient

from app.main import app

# TestClient wraps the FastAPI app so we can call endpoints in tests
# without starting a real HTTP server. Under the hood it uses the
# 'httpx' library to send requests directly to the app in-process.
client = TestClient(app)


def test_health_returns_200():
    """The /health endpoint should return HTTP 200 (OK)."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_body():
    """The /health endpoint should return the expected JSON payload."""
    response = client.get("/health")
    data = response.json()

    assert data["status"] == "healthy"
    assert data["service"] == "FinSight API"
    assert data["version"] == "0.1.0"
