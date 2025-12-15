"""
A file for unit/integration testing of API endpoints.

Task:
- Tests /api/analyze, /api/results and auth endpoints via TestClient (FastAPI).
- Uses a separate SQLite file or in-memory DB for the test database.

Note:
- Run tests via pytest for CI pipeline.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.api.v1 import deps
from app.db.session import SessionLocal, engine, get_db
from app.models.db_models import Base
import pytest

# Setup Test DB
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[deps.get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(scope="module")
def auth_header():
    # Register
    login_data = {"username": "testuser", "password": "password123"}
    client.post("/api/v1/auth/register", json={**login_data, "email": "test@example.com"})
    
    # Login
    response = client.post("/api/v1/auth/login", data=login_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to SecretSense API"}

import uuid

def test_register_login():
    # Use random username to avoid DB constraint errors on re-runs
    random_suffix = str(uuid.uuid4())[:8]
    username = f"user_{random_suffix}"
    email = f"user_{random_suffix}@example.com"
    password = "newp@ssword"
    
    response = client.post("/api/v1/auth/register", json={"username": username, "password": password, "email": email})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == username
    assert "id" in data

    response = client.post("/api/v1/auth/login", data={"username": username, "password": password})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_analyze_report(auth_header):
    # Mock SARIF report
    report_payload = {
        "tool": "gitleaks",
        "report": {
            "runs": [
                {
                    "tool": {"driver": {"name": "gitleaks", "rules": [{"id": "aws-key"}]}},
                    "results": [
                        {
                            "ruleId": "aws-key",
                            "message": {"text": "Found secret"},
                            "locations": [{"physicalLocation": {"artifactLocation": {"uri": "src/test_config.py"}, "region": {"snippet": {"text": "AKIAIOSFODNN7EXAMPLE"}}}}]
                        }
                    ]
                }
            ]
        }
    }
    
    response = client.post("/api/v1/analyze/", json=report_payload, headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert len(data["findings"]) == 1
    # Check heuristic logic was applied
    # "test_config.py" contains "test", so should be FP
    # "AKIAIOSFODNN7EXAMPLE" contains "EXAMPLE", so should be FP
    # Either way, verification.
    
    report_id = data["report_id"]
    
    # Test GET Results
    response_res = client.get(f"/api/v1/results/{report_id}", headers=auth_header)
    assert response_res.status_code == 200
    data_res = response_res.json()
    assert data_res["report_id"] == report_id

