from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from .config import AppConfig, SearchParams
from .github_client import GitHubClient


def build_search_query(params: SearchParams) -> str:
    """Build a GitHub search query for Rust repositories.

    Monoglot/polyglot classification is *not* encoded here; it will be
    derived later from per-repository language data.
    """

    parts = [f"language:{params.language}"]

    if params.min_stars > 0:
        parts.append(f"stars:>={params.min_stars}")
    if params.min_forks > 0:
        parts.append(f"forks:>={params.min_forks}")

    if params.created_from or params.created_to:
        if params.created_from and params.created_to:
            parts.append(f"created:{params.created_from}..{params.created_to}")
        elif params.created_from:
            parts.append(f"created:>={params.created_from}")
        else:
            parts.append(f"created:<={params.created_to}")

    return " ".join(parts)


def _minimal_repo_record(repo: Dict) -> Dict:
    """Extract a compact, JSON-serializable view of a repository.

    Detailed language breakdown, commits, issues, and CI data are collected
    in later stages; here we only store basic identifying metadata.
    """

    owner = repo.get("owner") or {}

    return {
        "id": repo.get("id"),
        "full_name": repo.get("full_name"),
        "name": repo.get("name"),
        "owner": owner.get("login"),
        "html_url": repo.get("html_url"),
        "default_branch": repo.get("default_branch"),
        "private": repo.get("private"),
        "fork": repo.get("fork"),
        "created_at": repo.get("created_at"),
        "pushed_at": repo.get("pushed_at"),
        "language": repo.get("language"),
        "stargazers_count": repo.get("stargazers_count"),
        "forks_count": repo.get("forks_count"),
        "open_issues_count": repo.get("open_issues_count"),
        # URLs for later stages of data collection
        "languages_url": repo.get("languages_url"),
        "issues_url": repo.get("issues_url"),
        "commits_url": repo.get("commits_url"),
    }


def discover_repositories(config: AppConfig, overwrite: bool = False) -> Path:
    """Query GitHub and persist the repository list as JSONL.

    Each line in the output file is a single repository record created by
    `_minimal_repo_record`. Existing records are preserved unless
    `overwrite=True` is passed.
    """

    repos_path = config.storage.repos_list_path
    repos_path.parent.mkdir(parents=True, exist_ok=True)

    client = GitHubClient(token=config.github_token)
    query = build_search_query(config.search)

    # Avoid duplicates when appending to an existing file.
    seen_ids = set()
    if repos_path.exists() and not overwrite:
        with repos_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                rid = obj.get("id")
                if isinstance(rid, int):
                    seen_ids.add(rid)

    mode = "w" if overwrite else ("a" if repos_path.exists() else "w")

    with repos_path.open(mode, encoding="utf-8") as fh:
        for repo in client.search_repositories(query=query):
            rid = repo.get("id")
            if isinstance(rid, int) and rid in seen_ids:
                continue

            record = _minimal_repo_record(repo)
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")

            if isinstance(rid, int):
                seen_ids.add(rid)

    return repos_path
