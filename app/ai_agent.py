import requests
from .config import settings
from typing import List, Dict
import os
import logging

GEMINI_API_KEY =  settings.OPENAI_API_KEY

def fetch_pr_files(repo_url: str, pr_number: int, github_token: str) -> List[Dict]:
    """
    Fetches the files changed in a GitHub PR.
    """
    api_url = repo_url.replace("https://github.com/", "https://api.github.com/repos/") + f"/pulls/{pr_number}/files"
    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        logging.error(f"Failed to fetch PR files: {response.status_code} - {response.text}")
        raise Exception("Failed to fetch PR files from GitHub.")
    
    return response.json()

def analyze_code(repo_url: str, pr_number: int, github_token: str) -> Dict:
    """
    Analyzes the code changes in a GitHub PR using OpenAI.
    """
    files = fetch_pr_files(repo_url, pr_number, github_token)
    issues = []
    critical_issues = 0

    for file in files:
        if file['status'] == 'removed':
            continue  # Skip removed files

        filename = file['filename']
        raw_url = file['raw_url']
        file_content = fetch_file_content(raw_url, github_token)
        language = detect_language(filename)
        
        analysis = perform_ai_analysis(file_content, language)
        file_issues, critical = parse_analysis(filename, analysis)
        issues.append({"name": filename, "issues": file_issues})
        critical_issues += critical

    summary = {
        "total_files": len(issues),
        "total_issues": sum(len(f['issues']) for f in issues),
        "critical_issues": critical_issues
    }

    return {"files": issues, "summary": summary}

def fetch_file_content(raw_url: str, github_token: str) -> str:
    """
    Fetches the raw content of a file from GitHub.
    """
    headers = {}
    if github_token:
        headers["Authorization"] = f"token {github_token}"
    
    response = requests.get(raw_url, headers=headers)
    if response.status_code != 200:
        logging.error(f"Failed to fetch file content: {response.status_code} - {response.text}")
        raise Exception("Failed to fetch file content from GitHub.")
    
    return response.text

def detect_language(filename: str) -> str:
    """
    Detects the programming language based on the file extension.
    """
    extension = os.path.splitext(filename)[1].lower()
    language_mapping = {
        ".py": "Python",
        ".js": "JavaScript",
        ".ts": "TypeScript",
        ".java": "Java",
        ".rb": "Ruby",
        ".go": "Go",
        ".cpp": "C++",
        ".c": "C",
        ".cs": "C#",
        ".php": "PHP",
        ".html": "HTML",
        ".css": "CSS",
        ".json": "JSON",
        ".xml": "XML",
        ".sql": "SQL",
        ".sh": "Shell Script",
        ".bat": "Batch File",
        ".swift": "Swift",
        ".kt": "Kotlin",
        ".rs": "Rust",
        ".r": "R",
        ".m": "MATLAB/Objective-C",
        ".pl": "Perl",
        ".lua": "Lua",
        ".scala": "Scala",
        ".dart": "Dart",
        ".groovy": "Groovy",
        ".hs": "Haskell",
        ".erl": "Erlang",
        ".ex": "Elixir",
        ".ml": "OCaml",
        ".vb": "Visual Basic",
        ".f90": "Fortran",
        ".asm": "Assembly",
        ".ps1": "PowerShell",
        ".tsx": "TypeScript JSX",
        ".jsx": "JavaScript JSX",
        ".md": "Markdown",
        ".yml": "YAML",
        ".toml": "TOML",
        ".ini": "INI File",
        ".yaml": "YAML",
        ".tsx": "TypeScript JSX",
        ".ipynb": "Jupyter Notebook",
        ".coffee": "CoffeeScript",
        # Add more mappings as needed
    }
    return language_mapping.get(extension, "Unknown")

# def perform_ai_analysis(code: str, language: str) -> str:
#     """
#     Uses OpenAI to analyze the code and identify issues.
#     """
#     prompt = f"""
#     You are a code review assistant. Analyze the following {language} code for:
#     - Code style and formatting issues
#     - Potential bugs or errors
#     - Performance improvements
#     - Best practices

#     Provide your feedback in JSON format with the following structure:

#     {{
#         "issues": [
#             {{
#                 "type": "style" | "bug" | "performance" | "best_practice",
#                 "line": <line_number>,
#                 "description": "<description>",
#                 "suggestion": "<suggestion>"
#             }},
#             ...
#         ]
#     }}
#     """
#     try:
#         response = openai.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant for code reviews."},
#                 {"role": "user", "content": prompt + "\n\n" + code}
#             ],
#             temperature=0.2,
#             max_tokens=1500,
#         )
#         analysis = response.choices[0].message['content']
#         return analysis
#     except Exception as e:
#         logging.error(f"OpenAI API error: {str(e)}")
#         raise e

def perform_ai_analysis(code: str, language: str) -> str:
    """
    Uses Gemini to analyze the code and identify issues via HTTP requests.
    """
    prompt = f"""
    You are a code review assistant. Analyze the following {language} code for:
    - Code style and formatting issues
    - Potential bugs or errors
    - Performance improvements
    - Best practices

    Provide your feedback in JSON format with the following structure:

    {{
        "issues": [
            {{
                "type": "style" | "bug" | "performance" | "best_practice",
                "line": <line_number>,
                "description": "<description>",
                "suggestion": "<suggestion>"
            }},
            ...
        ]
    }}
    """
    url = "https://api.gemini.com/v1/chat/completions"  # Hypothetical endpoint
    headers = {
        "Authorization": f"Bearer {GEMINI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gemini-1.0",  # Hypothetical model name
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for code reviews."},
            {"role": "user", "content": prompt + "\n\n" + code}
        ],
        "temperature": 0.2,
        "max_tokens": 1500,
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        analysis = data['choices'][0]['message']['content']
        return analysis
    except requests.exceptions.RequestException as e:
        logging.error(f"Gemini API request error: {str(e)}")
        raise e
    except KeyError:
        logging.error("Unexpected response format from Gemini API.")
        raise ValueError("Invalid response format")
    
def parse_analysis(filename: str, analysis: str) -> (List[Dict], int): # type: ignore
    """
    Parses the AI analysis JSON and returns issues and critical issue count.
    """
    try:
        import json
        data = json.loads(analysis)
        issues = data.get("issues", [])
        critical = sum(1 for issue in issues if issue["type"] == "bug")
        return issues, critical
    except json.JSONDecodeError:
        logging.error(f"Failed to parse AI analysis for {filename}")
        return [], 0