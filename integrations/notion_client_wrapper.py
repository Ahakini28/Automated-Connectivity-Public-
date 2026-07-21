"""Thin wrapper around the official Notion SDK for the databases the agents track."""

import os
from typing import Any

from notion_client import Client


class NotionWrapper:
    def __init__(self, api_key: str | None = None) -> None:
        api_key = api_key or os.environ.get("NOTION_API_KEY")
        if not api_key:
            raise ValueError("NOTION_API_KEY is not set")
        self.client = Client(auth=api_key)

    def query_database(
        self, database_id: str, filter_: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        kwargs: dict[str, Any] = {"database_id": database_id}
        if filter_:
            kwargs["filter"] = filter_
        results: list[dict[str, Any]] = []
        cursor = None
        while True:
            if cursor:
                kwargs["start_cursor"] = cursor
            response = self.client.databases.query(**kwargs)
            results.extend(response["results"])
            if not response.get("has_more"):
                break
            cursor = response["next_cursor"]
        return results

    def create_page(self, database_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        return self.client.pages.create(
            parent={"database_id": database_id}, properties=properties
        )

    def update_page(self, page_id: str, properties: dict[str, Any]) -> dict[str, Any]:
        return self.client.pages.update(page_id=page_id, properties=properties)

    def search(self, query: str) -> list[dict[str, Any]]:
        response = self.client.search(query=query)
        return response.get("results", [])
