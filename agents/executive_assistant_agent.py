"""Handles inbox triage, calendar scheduling, and file lookups on behalf of
the user via Gmail, Google Calendar, and Google Drive.
"""

from datetime import datetime, timedelta
from typing import Any

from agents.base_agent import BaseAgent
from integrations.google_client import GoogleWorkspaceClient


class ExecutiveAssistantAgent(BaseAgent):
    name = "ExecutiveAssistantAgent"

    def __init__(self, google: GoogleWorkspaceClient | None = None) -> None:
        super().__init__()
        self.google = google

    def get_daily_briefing(self) -> dict[str, Any]:
        if not self.google:
            return {"unread_email_count": 0, "todays_events": []}
        return {
            "unread_email_count": self.google.get_unread_count(),
            "todays_events": self.google.list_upcoming_events(hours_ahead=24),
        }

    def draft_reply(self, to: str, subject: str, body: str) -> dict[str, Any] | None:
        if not self.google:
            return None
        return self.google.create_draft(to, subject, body)

    def schedule_meeting(
        self, summary: str, start: datetime, duration_minutes: int = 30, attendees: list[str] | None = None
    ) -> dict[str, Any] | None:
        if not self.google:
            return None
        end = start + timedelta(minutes=duration_minutes)
        return self.google.create_event(summary, start, end, attendees=attendees)

    def find_files_for_topic(self, topic: str) -> list[dict[str, Any]]:
        if not self.google:
            return []
        return self.google.search_files(topic)

    def generate_report(self) -> dict[str, Any]:
        return {
            "agent": self.name,
            "briefing": self.get_daily_briefing(),
        }
