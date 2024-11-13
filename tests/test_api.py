
from fastapi.testclient import TestClient
from app.main import app
import pytest

client = TestClient(app)

@pytest.fixture
def mock_analyze_pr_task(monkeypatch):
    def mock_delay(*args, **kwargs):
        class MockTask:
            id = "test_task_id"
            status = "PENDING"
        return MockTask()
    monkeypatch.setattr("app.tasks.analyze_pr_task.delay", mock_delay)

def test_analyze_pr_endpoint(mock_analyze_pr_task):
    response = client.post("/analyze-pr", json={
        "repo_url": "https://github.com/user/repo",
        "pr_number": 1
    })
    assert response.status_code == 200
    assert response.json()["task_id"] == "test_task_id"
    assert response.json()["status"] == "PENDING"

def test_get_status_endpoint():
    response = client.get("/status/test_task_id")
    assert response.status_code == 200
    assert response.json()["status"] in ["pending", "processing", "completed", "failed", "unknown"]

def test_get_results_endpoint():
    response = client.get("/results/test_task_id")
    assert response.status_code == 404  # Since no results are storeds