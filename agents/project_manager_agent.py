"""Tracks project work across a Notion projects database and GitHub issues,
and schedules project meetings on Google Calendar.
"""

import os
from datetime import datetime, timedelta
from typing import Any

from agents.base_agent import BaseAgent
from integrations.github_client_wrapper import GitHubWrapper
from integrations.google_client import GoogleWorkspaceClient
from integrations.notion_client_wrapper import NotionWrapper


class ProjectManagerAgent(BaseAgent):
    name = "ProjectManagerAgent"

    def __init__(
        self,
        notion: NotionWrapper | None = None,
        github: GitHubWrapper | None = None,
        google: GoogleWorkspaceClient | None = None,
        repo_name: str | None = None,
        projects_db_id: str | None = None,
    ) -> None:
        super().__init__()
        self.notion = notion
        self.github = github
        self.google = google
        self.repo_name = repo_name or os.environ.get("GITHUB_REPO")
        self.projects_db_id = projects_db_id or os.environ.get("NOTION_PROJECTS_DB_ID")

    def create_project_task(
        self, title: str, assignee: str | None = None, due_date: str | None = None
    ) -> dict[str, Any] | None:
        if not self.notion or not self.projects_db_id:
            return None
        properties: dict[str, Any] = {"Name": {"title": [{"text": {"content": title}}]}}
        if assignee:
            properties["Assignee"] = {"rich_text": [{"text": {"content": assignee}}]}
        if due_date:
            properties["Due Date"] = {"date": {"start": due_date}}
        return self.notion.create_page(self.projects_db_id, properties)

    def sync_github_issues_to_notion(self) -> list[dict[str, Any]]:
        """Create a Notion project task for each open GitHub issue not already tracked."""
        if not self.github or not self.notion or not self.repo_name or not self.projects_db_id:
            return []
        existing_pages = self.notion.query_database(self.projects_db_id)
        existing_titles = {
            page["properties"]["Name"]["title"][0]["text"]["content"]
            for page in existing_pages
            if page["properties"].get("Name", {}).get("title")
        }
        created = []
        for issue in self.github.list_open_issues(self.repo_name):
            if issue["title"] not in existing_titles:
                created.append(self.create_project_task(issue["title"]))
        return created

    def get_upcoming_deadlines(self, days_ahead: int = 7) -> list[dict[str, Any]]:
        if not self.notion or not self.projects_db_id:
            return []
        pages = self.notion.query_database(self.projects_db_id)
        cutoff = (datetime.utcnow() + timedelta(days=days_ahead)).date().isoformat()
        deadlines = []
        for page in pages:
            due = page.get("properties", {}).get("Due Date", {}).get("date")
            if due and due.get("start") and due["start"] <= cutoff:
                deadlines.append({"id": page["id"], "url": page.get("url"), "due_date": due["start"]})
        return deadlines

    def schedule_project_meeting(
        self, summary: str, start: datetime, duration_minutes: int = 30, attendees: list[str] | None = None
    ) -> dict[str, Any] | None:
        if not self.google:
            return None
        end = start + timedelta(minutes=duration_minutes)
        return self.google.create_event(summary, start, end, attendees=attendees)

    def generate_report(self) -> dict[str, Any]:
        return {
            "agent": self.name,
            "upcoming_deadlines": self.get_upcoming_deadlines(),
            "open_issues": self.github.list_open_issues(self.repo_name)
            if self.github and self.repo_name
            else [],
        }
