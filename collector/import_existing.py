from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

from .config import load_config_from_env
from .db import DatabaseWriter
from .repo_data import load_repo_list


def _load_jsonl(path: Path):
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue


def import_repo_from_disk(db: DatabaseWriter, repo_record: Dict[str, Any], raw_root: Path) -> None:
    owner = repo_record.get("owner")
    name = repo_record.get("name")
    full_name = repo_record.get("full_name") or f"{owner}/{name}"

    if not owner or not name or not full_name:
        return

    repo_dir = raw_root / "github" / str(owner) / str(name)
    if not repo_dir.exists():
        # Nothing to import for this repo.
        return

    # Ensure repo exists in DB and clear any previous data to avoid duplicates.
    repo_id = db.mark_repo_started(repo_record)
    db.clear_repo_data(repo_id)

    # Commits.
    commits_path = repo_dir / "commits.jsonl"
    for commit in _load_jsonl(commits_path) or []:
        db.insert_commit(repo_id, commit)

    # Issues.
    issues_path = repo_dir / "issues.jsonl"
    for issue in _load_jsonl(issues_path) or []:
        db.insert_issue(repo_id, issue)

    # Workflows.
    workflows_path = repo_dir / "workflows.json"
    if workflows_path.exists():
        try:
            workflows_payload = json.loads(workflows_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            workflows_payload = {}
        for wf in (workflows_payload.get("workflows") or []):
            db.insert_workflow(repo_id, wf)

    # Workflow runs.
    workflow_runs_path = repo_dir / "workflow_runs.jsonl"
    for run in _load_jsonl(workflow_runs_path) or []:
        db.insert_workflow_run(repo_id, run)

    # Mark as completed once import is successful.
    db.mark_repo_completed(repo_record)


def main() -> int:
    cfg = load_config_from_env()
    db = DatabaseWriter.from_config(cfg)
    if db is None:
        raise SystemExit("RUST_CI_DB_DSN must be set to import into Postgres")

    repos_path = Path(cfg.storage.repos_list_path)
    if not repos_path.exists():
        raise SystemExit(f"Repository list not found: {repos_path}")

    raw_root = Path(cfg.storage.raw_data_root)

    count = 0
    for repo in load_repo_list(repos_path):
        import_repo_from_disk(db, repo, raw_root)
        count += 1

    print(f"[import] Imported data for {count} repositories.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
