from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List

import psycopg2
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


@dataclass
class DbConfig:
    dsn: str


def get_db_config() -> DbConfig:
    # Reuse the same DSN env var as the collector by default.
    dsn = os.getenv("RUST_CI_DB_DSN") or os.getenv(
        "UI_DB_DSN", "postgresql://rustci:rustci@db:5432/rustci"
    )
    return DbConfig(dsn=dsn)


def get_connection(cfg: DbConfig = Depends(get_db_config)):
    conn = psycopg2.connect(cfg.dsn)
    try:
        yield conn
    finally:
        conn.close()


app = FastAPI(title="Rust CI Stats UI")

# Templates live under ./templates
TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


@app.get("/", response_class=HTMLResponse)
def index(request: Request, conn=Depends(get_connection)):
    cur = conn.cursor()

    # Global table counts
    cur.execute("SELECT COUNT(*) FROM repos;")
    repos_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM commits;")
    commits_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM issues;")
    issues_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM workflows;")
    workflows_count = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM workflow_runs;")
    runs_count = cur.fetchone()[0]

    # Per-repo summary: basic metadata + counts per repo
    cur.execute(
        """
        SELECT
            r.id,
            r.owner,
            r.name,
            r.full_name,
            COALESCE(s.status, 'unknown') AS status,
            COALESCE(c.commit_count, 0) AS commit_count,
            COALESCE(i.issue_count, 0) AS issue_count,
            COALESCE(w.workflow_count, 0) AS workflow_count,
            COALESCE(runs.run_count, 0) AS run_count
        FROM repos r
        LEFT JOIN repo_collection_state s ON s.repo_id = r.id
        LEFT JOIN (
            SELECT repo_id, COUNT(*) AS commit_count
            FROM commits
            GROUP BY repo_id
        ) c ON c.repo_id = r.id
        LEFT JOIN (
            SELECT repo_id, COUNT(*) AS issue_count
            FROM issues
            GROUP BY repo_id
        ) i ON i.repo_id = r.id
        LEFT JOIN (
            SELECT repo_id, COUNT(*) AS workflow_count
            FROM workflows
            GROUP BY repo_id
        ) w ON w.repo_id = r.id
        LEFT JOIN (
            SELECT repo_id, COUNT(*) AS run_count
            FROM workflow_runs
            GROUP BY repo_id
        ) runs ON runs.repo_id = r.id
        ORDER BY
            CASE
                WHEN COALESCE(s.status, 'unknown') IN ('in_progress', 'completed')
                    THEN 0
                ELSE 1
            END,
            r.owner,
            r.name;
        """
    )

    repos: List[Dict[str, Any]] = []
    for row in cur.fetchall():
        (
            repo_id,
            owner,
            name,
            full_name,
            status,
            commit_count,
            issue_count,
            workflow_count,
            run_count,
        ) = row
        repos.append(
            {
                "id": repo_id,
                "owner": owner,
                "name": name,
                "full_name": full_name,
                "status": status,
                "commit_count": commit_count,
                "issue_count": issue_count,
                "workflow_count": workflow_count,
                "run_count": run_count,
            }
        )

    cur.close()

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "repos_count": repos_count,
            "commits_count": commits_count,
            "issues_count": issues_count,
            "workflows_count": workflows_count,
            "runs_count": runs_count,
            "repos": repos,
        },
    )


@app.get("/health", response_class=HTMLResponse)
def health(conn=Depends(get_connection)):
    # Simple DB connectivity check
    cur = conn.cursor()
    cur.execute("SELECT 1;")
    cur.fetchone()
    cur.close()
    return "ok"
