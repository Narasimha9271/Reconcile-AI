from fastapi.testclient import TestClient
from reconcileai.main import create_app

def test_healthz_returns_status_and_correlation_id():
    response = TestClient(create_app()).get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-Id"].startswith("req_")

def test_readyz_returns_safe_metadata():
    response = TestClient(create_app()).get("/readyz")
    assert response.json()["status"] == "ready"

def test_me_requires_identity_headers():
    response = TestClient(create_app()).get("/v1/me")
    assert response.status_code == 401

def test_me_returns_development_actor():
    response = TestClient(create_app()).get("/v1/me", headers={
        "X-Development-User-Id": "018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bc",
        "X-Development-Organization-Id": "018f1c43-68a1-7f1e-a7ec-0e8cf2ef72bd",
        "X-Development-Role": "ORG_ADMIN",
    })
    assert response.status_code == 200
    assert response.json()["role"] == "ORG_ADMIN"
