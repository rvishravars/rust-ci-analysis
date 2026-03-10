from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

import psycopg2
from psycopg2 import sql
from psycopg2.extras import Json

from .config import AppConfig, DatabaseConfig


@dataclass
class DatabaseWriter:
    """Helper for writing raw GitHub data and collection state to Postgres.

    This class is intentionally minimal and uses simple JSONB columns so we
    can store the GitHub payloads without complex schema mapping.
    """

    dsn: str

    def _connect(self):
        conn = psycopg2.connect(self.dsn)
        conn.autocommit = True
        return conn

    @classmethod
    def from_config(cls, config: AppConfig) -> Optional["DatabaseWriter"]:
        db_cfg: Optional[DatabaseConfig] = getattr(config, "db", None)
        if db_cfg is None or not db_cfg.dsn:
            return None
        writer = cls(dsn=db_cfg.dsn)
        # Ensure schema exists up-front so later writes are cheap.
        writer.ensure_schema()
        return writer

    def ensure_schema(self) -> None:
        conn = self._connect()
        try:
            cur = conn.cursor()

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS repos (
                    id BIGINT PRIMARY KEY,
                    full_name TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    owner TEXT NOT NULL,
                    html_url TEXT,
                    metadata JSONB,
                    collected_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS repo_collection_state (
                    repo_id BIGINT PRIMARY KEY REFERENCES repos(id) ON DELETE CASCADE,
                    status TEXT NOT NULL,
                    last_error TEXT,
                    updated_at TIMESTAMPTZ DEFAULT NOW(),
                    last_collected_at TIMESTAMPTZ
                );
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS commits (
                    id BIGSERIAL PRIMARY KEY,
                    repo_id BIGINT REFERENCES repos(id) ON DELETE CASCADE,
                    sha TEXT,
                    data JSONB
                );
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS issues (
                    id BIGSERIAL PRIMARY KEY,
                    repo_id BIGINT REFERENCES repos(id) ON DELETE CASCADE,
                    number BIGINT,
                    data JSONB
                );
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS workflows (
                    id BIGSERIAL PRIMARY KEY,
                    repo_id BIGINT REFERENCES repos(id) ON DELETE CASCADE,
                    workflow_id BIGINT,
                    data JSONB
                );
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS workflow_runs (
                    id BIGSERIAL PRIMARY KEY,
                    repo_id BIGINT REFERENCES repos(id) ON DELETE CASCADE,
                    run_id BIGINT,
                    data JSONB
                );
                """
            )

            cur.close()
        finally:
            conn.close()

    # --- Repo and state helpers -------------------------------------------------

    def _get_or_create_repo(self, repo_record: Dict[str, Any]) -> int:
        repo_id = int(repo_record.get("id"))
        full_name = str(repo_record.get("full_name"))
        name = str(repo_record.get("name"))
        owner = str(repo_record.get("owner"))
        html_url = repo_record.get("html_url")

        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO repos (id, full_name, name, owner, html_url, metadata)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    full_name = EXCLUDED.full_name,
                    name = EXCLUDED.name,
                    owner = EXCLUDED.owner,
                    html_url = EXCLUDED.html_url,
                    metadata = EXCLUDED.metadata,
                    collected_at = NOW()
                RETURNING id;
                """,
                (repo_id, full_name, name, owner, html_url, Json(repo_record)),
            )
            row = cur.fetchone()
            cur.close()
            return int(row[0])
        finally:
            conn.close()

    def is_repo_completed(self, full_name: str) -> bool:
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT s.status
                FROM repo_collection_state s
                JOIN repos r ON r.id = s.repo_id
                WHERE r.full_name = %s;
                """,
                (full_name,),
            )
            row = cur.fetchone()
            cur.close()
            if not row:
                return False
            return row[0] == "completed"
        finally:
            conn.close()

    def mark_repo_started(self, repo_record: Dict[str, Any]) -> int:
        repo_id = self._get_or_create_repo(repo_record)
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO repo_collection_state (repo_id, status, last_error, updated_at)
                VALUES (%s, 'in_progress', NULL, NOW())
                ON CONFLICT (repo_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    last_error = EXCLUDED.last_error,
                    updated_at = EXCLUDED.updated_at;
                """,
                (repo_id,),
            )
            cur.close()
            return repo_id
        finally:
            conn.close()

    def mark_repo_completed(self, repo_record: Dict[str, Any]) -> None:
        repo_id = self._get_or_create_repo(repo_record)
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO repo_collection_state (repo_id, status, last_error, updated_at, last_collected_at)
                VALUES (%s, 'completed', NULL, NOW(), NOW())
                ON CONFLICT (repo_id) DO UPDATE SET
                    status = EXCLUDED.status,
                    last_error = EXCLUDED.last_error,
                    updated_at = EXCLUDED.updated_at,
                    last_collected_at = EXCLUDED.last_collected_at;
                """,
                (repo_id,),
            )
            cur.close()
        finally:
            conn.close()

    # --- Data write helpers -----------------------------------------------------

    def clear_repo_data(self, repo_id: int) -> None:
        conn = self._connect()
        try:
            cur = conn.cursor()
            for table in ("commits", "issues", "workflows", "workflow_runs"):
                cur.execute(sql.SQL("DELETE FROM {} WHERE repo_id = %s;").format(sql.Identifier(table)), (repo_id,))
            cur.close()
        finally:
            conn.close()

    def insert_commit(self, repo_id: int, commit: Dict[str, Any]) -> None:
        sha = commit.get("sha")
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO commits (repo_id, sha, data)
                VALUES (%s, %s, %s);
                """,
                (repo_id, sha, Json(commit)),
            )
            cur.close()
        finally:
            conn.close()

    def insert_issue(self, repo_id: int, issue: Dict[str, Any]) -> None:
        number = issue.get("number")
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO issues (repo_id, number, data)
                VALUES (%s, %s, %s);
                """,
                (repo_id, number, Json(issue)),
            )
            cur.close()
        finally:
            conn.close()

    def insert_workflow(self, repo_id: int, workflow: Dict[str, Any]) -> None:
        workflow_id = workflow.get("id")
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO workflows (repo_id, workflow_id, data)
                VALUES (%s, %s, %s);
                """,
                (repo_id, workflow_id, Json(workflow)),
            )
            cur.close()
        finally:
            conn.close()

    def insert_workflow_run(self, repo_id: int, run: Dict[str, Any]) -> None:
        run_id = run.get("id")
        conn = self._connect()
        try:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO workflow_runs (repo_id, run_id, data)
                VALUES (%s, %s, %s);
                """,
                (repo_id, run_id, Json(run)),
            )
            cur.close()
        finally:
            conn.close()
