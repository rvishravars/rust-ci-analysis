from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Iterable, Optional

from .config import AppConfig
from .github_client import GitHubClient


def _ensure_repo_dir(config: AppConfig, owner: str, name: str) -> Path:
    base = config.storage.raw_data_root
    repo_dir = base / "github" / owner / name
    repo_dir.mkdir(parents=True, exist_ok=True)
    return repo_dir


def _write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_jsonl(path: Path, items: Iterable[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for item in items:
            fh.write(json.dumps(item, ensure_ascii=False) + "\n")


def _iter_commits(client: GitHubClient, full_name: str) -> Iterable[Dict[str, Any]]:
    path = f"/repos/{full_name}/commits"
    page = 1
    per_page = 100

    while True:
        params = {"per_page": per_page, "page": page}
        response = client.get(path, params=params)
        page_items = response.json() or []
        if not page_items:
            break

        for item in page_items:
            yield item

        if len(page_items) < per_page:
            break

        page += 1


def _iter_issues(client: GitHubClient, full_name: str) -> Iterable[Dict[str, Any]]:
    path = f"/repos/{full_name}/issues"
    page = 1
    per_page = 100

    while True:
        params = {"per_page": per_page, "page": page, "state": "all"}
        response = client.get(path, params=params)
        page_items = response.json() or []
        if not page_items:
            break

        for item in page_items:
            # Pull requests also appear in /issues; keep them for now so
            # later analytics can distinguish if needed.
            yield item

        if len(page_items) < per_page:
            break

        page += 1


def _iter_workflow_runs(client: GitHubClient, full_name: str) -> Iterable[Dict[str, Any]]:
    path = f"/repos/{full_name}/actions/runs"
    page = 1
    per_page = 100

    while True:
        params = {"per_page": per_page, "page": page}
        response = client.get(path, params=params)
        payload = response.json() or {}
        runs = payload.get("workflow_runs") or []
        if not runs:
            break

        for item in runs:
            yield item

        if len(runs) < per_page:
            break

        page += 1


def collect_repo_raw_data(
    config: AppConfig,
    repo_record: Dict[str, Any],
    client: Optional[GitHubClient] = None,
) -> Path:
    """Download raw metadata and CI-related data for a single repository.

    This function does *not* perform any analytics; it only persists JSON
    responses to disk for later processing.
    """

    owner = repo_record.get("owner")
    name = repo_record.get("name")
    full_name = repo_record.get("full_name")

    if not owner or not name or not full_name:
        raise ValueError("repo_record must include 'owner', 'name', and 'full_name'")

    if client is None:
        client = GitHubClient(token=config.github_token)

    repo_dir = _ensure_repo_dir(config, owner, name)

    # Persist the basic repository record as-is.
    _write_json(repo_dir / "repo.json", repo_record)

    # Languages breakdown.
    languages_resp = client.get(f"/repos/{full_name}/languages")
    _write_json(repo_dir / "languages.json", languages_resp.json())

    # Commit history (for later velocity and CI-adoption analysis).
    _write_jsonl(repo_dir / "commits.jsonl", _iter_commits(client, full_name))

    # Issues and pull requests (for later bug/defect metrics).
    _write_jsonl(repo_dir / "issues.jsonl", _iter_issues(client, full_name))

    # CI configuration: GitHub Actions workflows.
    workflows_resp = client.get(f"/repos/{full_name}/actions/workflows")
    _write_json(repo_dir / "workflows.json", workflows_resp.json())

    # CI execution metadata: workflow runs.
    _write_jsonl(
        repo_dir / "workflow_runs.jsonl",
        _iter_workflow_runs(client, full_name),
    )

    return repo_dir


def load_repo_list(path: Path) -> Iterable[Dict[str, Any]]:
    """Load repository records from a JSONL file created by discovery."""

    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                continue
