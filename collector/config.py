from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
import os


@dataclass
class SearchParams:
    """Configuration for discovering Rust repositories.

    This only defines *what to look for*; no network logic here.
    """

    language: str = "Rust"
    min_stars: int = 0
    min_forks: int = 0
    created_from: Optional[str] = None  # e.g. "2015-01-01"
    created_to: Optional[str] = None    # e.g. "2025-12-31"
    monoglot_only: bool = False
    polyglot_only: bool = False


@dataclass
class StorageConfig:
    """Filesystem layout for storing collected data.

    All paths are absolute and point to *raw* (non-aggregated) data.
    """

    repos_list_path: Path
    raw_data_root: Path


@dataclass
class DatabaseConfig:
    """Database configuration for optional Postgres storage.

    When configured, the collector will persist raw GitHub data and
    per-repository collection state into a local Postgres instance.
    """

    dsn: str


@dataclass
class AppConfig:
    """Top-level configuration for the Rust CI data collector.

    This bundles search parameters, storage locations, and secrets.
    """

    github_token: str
    search: SearchParams
    storage: StorageConfig
    db: Optional[DatabaseConfig] = None


def _get_bool_env(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def load_config_from_env() -> AppConfig:
    """Load configuration from environment variables with sane defaults.

    Environment variables used:
      - GITHUB_TOKEN (required): personal access token for GitHub API.
      - RUST_CI_MIN_STARS (int, optional)
      - RUST_CI_MIN_FORKS (int, optional)
      - RUST_CI_CREATED_FROM (YYYY-MM-DD, optional)
      - RUST_CI_CREATED_TO (YYYY-MM-DD, optional)
      - RUST_CI_MONOGLOT_ONLY (bool, optional)
      - RUST_CI_POLYGLOT_ONLY (bool, optional)
      - RUST_CI_DATA_DIR (path, optional; default: ./data)
      - RUST_CI_REPOS_LIST (path, optional; default: <DATA_DIR>/repos.jsonl)
    - RUST_CI_RAW_ROOT (path, optional; default: <DATA_DIR>/raw)
    - RUST_CI_DB_DSN (Postgres DSN, optional; when set enables DB storage)
    """

    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("GITHUB_TOKEN environment variable must be set")

    min_stars = int(os.getenv("RUST_CI_MIN_STARS", "0"))
    min_forks = int(os.getenv("RUST_CI_MIN_FORKS", "0"))
    created_from = os.getenv("RUST_CI_CREATED_FROM") or None
    created_to = os.getenv("RUST_CI_CREATED_TO") or None

    monoglot_only = _get_bool_env("RUST_CI_MONOGLOT_ONLY", default=False)
    polyglot_only = _get_bool_env("RUST_CI_POLYGLOT_ONLY", default=False)

    data_dir_env = os.getenv("RUST_CI_DATA_DIR", "data")
    data_dir = Path(data_dir_env).expanduser().resolve()

    repos_list_env = os.getenv("RUST_CI_REPOS_LIST")
    if repos_list_env is None:
        repos_list_path = data_dir / "repos.jsonl"
    else:
        repos_list_path = Path(repos_list_env).expanduser().resolve()

    raw_root_env = os.getenv("RUST_CI_RAW_ROOT")
    if raw_root_env is None:
        raw_data_root = data_dir / "raw"
    else:
        raw_data_root = Path(raw_root_env).expanduser().resolve()

    search = SearchParams(
        language="Rust",
        min_stars=min_stars,
        min_forks=min_forks,
        created_from=created_from,
        created_to=created_to,
        monoglot_only=monoglot_only,
        polyglot_only=polyglot_only,
    )

    storage = StorageConfig(
        repos_list_path=repos_list_path,
        raw_data_root=raw_data_root,
    )

    db_dsn = os.getenv("RUST_CI_DB_DSN") or None
    db_cfg: Optional[DatabaseConfig]
    if db_dsn:
        db_cfg = DatabaseConfig(dsn=db_dsn)
    else:
        db_cfg = None

    return AppConfig(
        github_token=token,
        search=search,
        storage=storage,
        db=db_cfg,
    )
