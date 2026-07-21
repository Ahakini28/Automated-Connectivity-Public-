"""Demo entry point: builds the four agents and prints a combined dashboard.

Each integration client is optional — an agent falls back to empty results
for any service that isn't configured, so this runs even with a partial
.env setup.
"""

import os

from dotenv import load_dotenv

from agents.dashboard_agent import DashboardAgent
from agents.executive_assistant_agent import ExecutiveAssistantAgent
from agents.operations_agent import OperationsAgent
from agents.project_manager_agent import ProjectManagerAgent
from integrations.github_client_wrapper import GitHubWrapper
from integrations.google_client import GoogleWorkspaceClient
from integrations.notion_client_wrapper import NotionWrapper


def build_client_or_none(factory):
    try:
        return factory()
    except Exception as exc:
        print(f"Skipping integration ({exc})")
        return None


def main() -> None:
    load_dotenv()

    github = build_client_or_none(GitHubWrapper) if os.environ.get("GITHUB_TOKEN") else None
    notion = build_client_or_none(NotionWrapper) if os.environ.get("NOTION_API_KEY") else None
    google = (
        build_client_or_none(GoogleWorkspaceClient)
        if os.path.exists(os.environ.get("GOOGLE_CREDENTIALS_PATH", "credentials.json"))
        else None
    )

    operations_agent = OperationsAgent(github=github, notion=notion)
    project_manager_agent = ProjectManagerAgent(notion=notion, github=github, google=google)
    executive_assistant_agent = ExecutiveAssistantAgent(google=google)

    dashboard_agent = DashboardAgent(
        operations_agent, project_manager_agent, executive_assistant_agent
    )
    print(dashboard_agent.render_console())


if __name__ == "__main__":
    main()
