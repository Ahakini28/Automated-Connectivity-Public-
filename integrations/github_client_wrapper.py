"""Thin wrapper around PyGithub for the repo activity the agents track."""

import os
from typing import Any

from github import Github


class GitHubWrapper:
    def __init__(self, token: str | None = None) -> None:
        token = token or os.environ.get("GITHUB_TOKEN")
        if not token:
            raise ValueError("GITHUB_TOKEN is not set")
        self.client = Github(token)

    def list_open_issues(self, repo_name: str) -> list[dict[str, Any]]:
        repo = self.client.get_repo(repo_name)
        return [
            {
                "number": issue.number,
                "title": issue.title,
                "url": issue.html_url,
                "assignee": issue.assignee.login if issue.assignee else None,
                "labels": [label.name for label in issue.labels],
            }
            for issue in repo.get_issues(state="open")
            if issue.pull_request is None
        ]

    def list_open_pull_requests(self, repo_name: str) -> list[dict[str, Any]]:
        repo = self.client.get_repo(repo_name)
        return [
            {
                "number": pr.number,
                "title": pr.title,
                "url": pr.html_url,
                "mergeable_state": pr.mergeable_state,
                "draft": pr.draft,
            }
            for pr in repo.get_pulls(state="open")
        ]

    def get_recent_workflow_runs(
        self, repo_name: str, max_results: int = 10
    ) -> list[dict[str, Any]]:
        repo = self.client.get_repo(repo_name)
        runs = repo.get_workflow_runs()[:max_results]
        return [
            {
                "name": run.name,
                "status": run.status,
                "conclusion": run.conclusion,
                "url": run.html_url,
                "created_at": run.created_at.isoformat(),
            }
            for run in runs
        ]

    def create_issue(
        self, repo_name: str, title: str, body: str = "", labels: list[str] | None = None
    ) -> dict[str, Any]:
        repo = self.client.get_repo(repo_name)
        issue = repo.create_issue(title=title, body=body, labels=labels or [])
        return {"number": issue.number, "url": issue.html_url}
