"""Monitors day-to-day operational health: CI status, open issues/PRs, and
overdue tasks tracked in a Notion operations database.
"""

import os
from datetime import date
from typing import Any

from agents.base_agent import BaseAgent
from integrations.github_client_wrapper import GitHubWrapper
from integrations.notion_client_wrapper import NotionWrapper


class OperationsAgent(BaseAgent):
    name = "OperationsAgent"

    def __init__(
        self,
        github: GitHubWrapper | None = None,
        notion: NotionWrapper | None = None,
        repo_name: str | None = None,
        operations_db_id: str | None = None,
    ) -> None:
        super().__init__()
        self.github = github
        self.notion = notion
        self.repo_name = repo_name or os.environ.get("GITHUB_REPO")
        self.operations_db_id = operations_db_id or os.environ.get("NOTION_OPERATIONS_DB_ID")

    def check_ci_health(self) -> list[dict[str, Any]]:
        if not self.github or not self.repo_name:
            return []
        return self.github.get_recent_workflow_runs(self.repo_name)

    def get_open_issues_summary(self) -> dict[str, Any]:
        if not self.github or not self.repo_name:
            return {"issues": [], "pull_requests": []}
        return {
            "issues": self.github.list_open_issues(self.repo_name),
            "pull_requests": self.github.list_open_pull_requests(self.repo_name),
        }

    def get_overdue_tasks(self) -> list[dict[str, Any]]:
        """Pages in the operations DB whose "Due Date" is in the past and
        "Status" is not "Done". Assumes that property schema.
        """
        if not self.notion or not self.operations_db_id:
            return []
        pages = self.notion.query_database(self.operations_db_id)
        overdue = []
        today = date.today().isoformat()
        for page in pages:
            props = page.get("properties", {})
            due = props.get("Due Date", {}).get("date")
            status = props.get("Status", {}).get("status", {})
            status_name = status.get("name") if status else None
            if due and due.get("start", "9999-12-31") < today and status_name != "Done":
                overdue.append(
                    {
                        "id": page["id"],
                        "url": page.get("url"),
                        "due_date": due.get("start"),
                        "status": status_name,
                    }
                )
        return overdue

    def generate_report(self) -> dict[str, Any]:
        issues_summary = self.get_open_issues_summary()
        return {
            "agent": self.name,
            "ci_runs": self.check_ci_health(),
            "open_issues": issues_summary["issues"],
            "open_pull_requests": issues_summary["pull_requests"],
            "overdue_tasks": self.get_overdue_tasks(),
        }
