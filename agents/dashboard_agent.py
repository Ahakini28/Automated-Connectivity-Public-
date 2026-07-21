"""Aggregates reports from the other agents into a single status snapshot."""

import json
from datetime import datetime, timezone
from typing import Any

from agents.base_agent import BaseAgent
from agents.executive_assistant_agent import ExecutiveAssistantAgent
from agents.operations_agent import OperationsAgent
from agents.project_manager_agent import ProjectManagerAgent


class DashboardAgent(BaseAgent):
    name = "DashboardAgent"

    def __init__(
        self,
        operations_agent: OperationsAgent,
        project_manager_agent: ProjectManagerAgent,
        executive_assistant_agent: ExecutiveAssistantAgent,
    ) -> None:
        super().__init__()
        self.operations_agent = operations_agent
        self.project_manager_agent = project_manager_agent
        self.executive_assistant_agent = executive_assistant_agent

    def generate_report(self) -> dict[str, Any]:
        return {
            "agent": self.name,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "operations": self.operations_agent.generate_report(),
            "projects": self.project_manager_agent.generate_report(),
            "executive_assistant": self.executive_assistant_agent.generate_report(),
        }

    def render_json(self) -> str:
        return json.dumps(self.generate_report(), indent=2, default=str)

    def render_console(self) -> str:
        report = self.generate_report()
        lines = [f"=== Dashboard ({report['generated_at']}) ==="]

        ops = report["operations"]
        lines.append(f"\n[Operations] {len(ops['open_issues'])} open issues, "
                      f"{len(ops['open_pull_requests'])} open PRs, "
                      f"{len(ops['overdue_tasks'])} overdue tasks")

        projects = report["projects"]
        lines.append(f"[Projects] {len(projects['upcoming_deadlines'])} deadlines in the next 7 days")

        ea = report["executive_assistant"]["briefing"]
        lines.append(f"[Executive Assistant] {ea['unread_email_count']} unread emails, "
                      f"{len(ea['todays_events'])} events in the next 24h")

        return "\n".join(lines)
