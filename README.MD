# Autonomous Code Review Agent

## Overview

An autonomous code review agent system that uses AI to analyze GitHub pull requests. The system processes analyses asynchronously using Celery and interacts with developers through a structured API.

## Features

- Analyze code style, potential bugs, performance improvements, and best practices.
- Asynchronous task processing with Celery.
- Structured API with FastAPI.
- Caching of results to optimize performance.
- Dockerized setup for easy deployment.
- Support for multiple programming languages.

## Setup Instructions

### Prerequisites

- Python 3.8+
- Docker and Docker Compose
- Git

### Clone the Repository

```bash
git clone https://github.com/yourusername/code_review_agent.git
cd code_review_agent