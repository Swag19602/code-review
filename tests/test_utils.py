from app.utils import store_results, get_task_results
import json

def test_store_and_get_results():
    task_id = "test_task"
    results = {"key": "value"}
    store_results(task_id, results)
    retrieved = get_task_results(task_id)
    assert retrieved == results