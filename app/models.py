# app/models.py
from pydantic import BaseModel, HttpUrl
from typing import Optional

class AnalyzePRRequest(BaseModel):
    repo_url: HttpUrl
    pr_number: int
    github_token: Optional[str] = None

class Issue(BaseModel):
    type: str
    line: int
    description: str
    suggestion: str

class FileIssues(BaseModel):
    name: str
    issues: list[Issue]

class Summary(BaseModel):
    total_files: int
    total_issues: int
    critical_issues: int

class AnalyzePRResult(BaseModel):
    task_id: str
    status: str
    results: Optional[dict] = None