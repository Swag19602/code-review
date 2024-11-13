# app/api.py
from fastapi import APIRouter, HTTPException, Depends
from .models import AnalyzePRRequest, AnalyzePRResult
from .tasks import analyze_pr_task
from celery.result import AsyncResult
from .utils import get_task_results

router = APIRouter()

@router.post("/analyze-pr", response_model=AnalyzePRResult)
def analyze_pr(request: AnalyzePRRequest):
    task = analyze_pr_task.delay(request.repo_url, request.pr_number, request.github_token or "")
    return AnalyzePRResult(task_id=task.id, status=task.status)

@router.get("/status/{task_id}")
def get_status(task_id: str):
    task_result = AsyncResult(task_id)
    status_mapping = {
        "PENDING": "pending",
        "STARTED": "processing",
        "SUCCESS": "completed",
        "FAILURE": "failed"
    }
    status = status_mapping.get(task_result.state, "unknown")
    return {"status": status}

@router.get("/results/{task_id}")
def get_results(task_id: str):
    results = get_task_results(task_id)
    if not results:
        raise HTTPException(status_code=404, detail="Results not found or task not completed.")
    return results