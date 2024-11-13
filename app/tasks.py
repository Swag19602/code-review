# app/tasks.py
from celery import Celery
from .config import settings
from .ai_agent import analyze_code
from .utils import store_results
import logging
from .utils import store_results, get_cached_results, set_cached_results

celery_app = Celery(
    "tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.task_routes = {
    "app.tasks.analyze_pr_task": "code_review_tasks"
}

@celery_app.task(bind=True, name="app.tasks.analyze_pr_task")
def analyze_pr_task(self, repo_url: str, pr_number: int, github_token: str):
    try:
        logging.info(f"Starting analysis for PR #{pr_number} in {repo_url}")
        results = analyze_code(repo_url, pr_number, github_token)
        store_results(self.request.id, results)
        logging.info(f"Completed analysis for PR #{pr_number} in {repo_url}")
        return results
    except Exception as e:
        logging.error(f"Error analyzing PR: {str(e)}")
        self.retry(exc=e, countdown=60, max_retries=3)

@celery_app.task(bind=True, name="app.tasks.analyze_pr_task")
def analyze_pr_task(self, repo_url: str, pr_number: int, github_token: str):
    try:
        # Check if results are cached
        cached = get_cached_results(repo_url, pr_number)
        if cached:
            logging.info(f"Using cached results for PR #{pr_number} in {repo_url}")
            return cached

        logging.info(f"Starting analysis for PR #{pr_number} in {repo_url}")
        results = analyze_code(repo_url, pr_number, github_token)
        store_results(self.request.id, results)
        set_cached_results(repo_url, pr_number, results)
        logging.info(f"Completed analysis for PR #{pr_number} in {repo_url}")
        return results
    except Exception as e:
        logging.error(f"Error analyzing PR: {str(e)}")
        self.retry(exc=e, countdown=60, max_retries=3)