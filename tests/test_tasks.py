# tests/test_tasks.py
from app.tasks import analyze_pr_task
from unittest.mock import patch

@patch("app.ai_agent.analyze_code")
@patch("app.utils.store_results")
def test_analyze_pr_task(mock_store_results, mock_analyze_code):
    mock_analyze_code.return_value = {
        "files": [],
        "summary": {
            "total_files": 0,
            "total_issues": 0,
            "critical_issues": 0
        }
    }
    result = analyze_pr_task("https://github.com/user/repo", 1, "token")
    mock_analyze_code.assert_called_once()
    mock_store_results.assert_called_once()
    assert result["summary"]["total_issues"] == 0