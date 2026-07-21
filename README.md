# Automated-Connectivity-Public-
Automated Connectivity
A small multi-agent quandrant with four agents that share a common set of integrations (Gmail, Google Calendar, Google Drive, Notion, GitHub):

OperationsAgent — CI health, open issues/PRs, overdue Notion ops tasks.
ProjectManagerAgent — Notion project tracking, GitHub issue sync, deadlines, meeting scheduling.
ExecutiveAssistantAgent — inbox briefing, draft replies, calendar scheduling, Drive lookups.
DashboardAgent — aggregates the other three agents' reports into one snapshot (JSON or console).

# LAY OUT
agents/            Agent classes (one per agent above), all implementing BaseAgent.generate_report()
integrations/      Thin wrappers around the Google, Notion, and GitHub SDKs
main.py            Demo: builds whichever integrations are configured and prints a dashboard

# SET UP 
pip install -r requirements.txt
cp .env.example .env   # fill in the values you have
python main.py
Each integration is optional — main.py only builds a client for a service if its credentials are present in the environment, and every agent method degrades to an empty result when its underlying client is None. This lets you run the dashboard with, say, only GitHub configured.

Google (Gmail / Calendar / Drive)
Create an OAuth client ID (Desktop app) in Google Cloud Console.
Download it as credentials.json in the repo root (or point GOOGLE_CREDENTIALS_PATH at it).
First run opens a browser consent screen; the resulting token is cached at GOOGLE_TOKEN_PATH (token.json by default).

# NOTION
Create an internal integration at https://www.notion.so/my-integrations.
Share the operations/projects databases with it.
Set NOTION_API_KEY, NOTION_OPERATIONS_DB_ID, NOTION_PROJECTS_DB_ID.
The operations/projects database schemas are assumed to have Name (title), Status (status), Due Date (date), and Assignee (rich text) properties — adjust the property names in agents/operations_agent.py and agents/project_manager_agent.py if your databases differ.

# GIT HUB
Set GITHUB_TOKEN (repo + workflow scopes) and GITHUB_REPO (owner/repo).

# STATUS
This is preliminary scaffolding: the integration wrappers cover the calls each agent currently needs, and each agent covers one report/action set. Extend by adding methods to the relevant wrapper and agent as new capabilities are needed.
