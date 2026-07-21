"""Thin wrapper around the Gmail, Calendar, and Drive APIs.

Auth uses a standard OAuth "installed app" flow: the first run opens a
browser consent screen and caches the resulting token at GOOGLE_TOKEN_PATH
for subsequent runs.
"""

import os
from datetime import datetime, timedelta, timezone
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/drive.readonly",
]


class GoogleWorkspaceClient:
    def __init__(
        self,
        credentials_path: str | None = None,
        token_path: str | None = None,
    ) -> None:
        self.credentials_path = credentials_path or os.environ.get(
            "GOOGLE_CREDENTIALS_PATH", "credentials.json"
        )
        self.token_path = token_path or os.environ.get("GOOGLE_TOKEN_PATH", "token.json")
        creds = self._load_credentials()
        self.gmail = build("gmail", "v1", credentials=creds)
        self.calendar = build("calendar", "v3", credentials=creds)
        self.drive = build("drive", "v3", credentials=creds)

    def _load_credentials(self) -> Credentials:
        creds = None
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            with open(self.token_path, "w") as token_file:
                token_file.write(creds.to_json())
        return creds

    # -- Gmail -----------------------------------------------------------

    def search_emails(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        response = (
            self.gmail.users()
            .messages()
            .list(userId="me", q=query, maxResults=max_results)
            .execute()
        )
        messages = response.get("messages", [])
        return [
            self.gmail.users()
            .messages()
            .get(userId="me", id=msg["id"], format="metadata")
            .execute()
            for msg in messages
        ]

    def get_unread_count(self) -> int:
        label = (
            self.gmail.users()
            .labels()
            .get(userId="me", id="UNREAD")
            .execute()
        )
        return label.get("messagesUnread", 0)

    def create_draft(self, to: str, subject: str, body: str) -> dict[str, Any]:
        import base64
        from email.mime.text import MIMEText

        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        return (
            self.gmail.users()
            .drafts()
            .create(userId="me", body={"message": {"raw": raw}})
            .execute()
        )

    # -- Calendar ----------------------------------------------------------

    def list_upcoming_events(
        self, calendar_id: str = "primary", max_results: int = 10, hours_ahead: int = 24
    ) -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc)
        time_max = now + timedelta(hours=hours_ahead)
        response = (
            self.calendar.events()
            .list(
                calendarId=calendar_id,
                timeMin=now.isoformat(),
                timeMax=time_max.isoformat(),
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return response.get("items", [])

    def create_event(
        self,
        summary: str,
        start: datetime,
        end: datetime,
        attendees: list[str] | None = None,
        calendar_id: str = "primary",
    ) -> dict[str, Any]:
        event = {
            "summary": summary,
            "start": {"dateTime": start.isoformat()},
            "end": {"dateTime": end.isoformat()},
            "attendees": [{"email": email} for email in (attendees or [])],
        }
        return self.calendar.events().insert(calendarId=calendar_id, body=event).execute()

    # -- Drive -------------------------------------------------------------

    def search_files(self, query: str, max_results: int = 10) -> list[dict[str, Any]]:
        escaped_query = query.replace("\\", "\\\\").replace("'", "\\'")
        response = (
            self.drive.files()
            .list(
                q=f"name contains '{escaped_query}' and trashed = false",
                pageSize=max_results,
                fields="files(id, name, mimeType, modifiedTime, webViewLink)",
            )
            .execute()
        )
        return response.get("files", [])
