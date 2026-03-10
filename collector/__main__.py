from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .config import load_config_from_env
from .repo_discovery import discover_repositories
from .repo_data import collect_repo_raw_data, load_repo_list


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Regather Rust CI study repositories and raw data.",
    )
    parser.add_argument(
        "--overwrite-repos-list",
        action="store_true",
        help="Regenerate the repositories list file instead of appending.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum number of repositories to collect (for smoke tests).",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help=(
            "Skip repositories that already have a repo.json under "
            "the raw data directory."
        ),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    cfg = load_config_from_env()

    print("[collector] Discovering repositories…", flush=True)
    repos_path = discover_repositories(cfg, overwrite=args.overwrite_repos_list)
    print(f"[collector] Repository list written to: {repos_path}", flush=True)

    # Iterate over repositories and collect raw data.
    count = 0
    for repo in load_repo_list(Path(repos_path)):
        owner = repo.get("owner")
        name = repo.get("name")
        if not owner or not name:
            continue

        repo_dir = (
            cfg.storage.raw_data_root
            / "github"
            / str(owner)
            / str(name)
        )

        if args.resume and (repo_dir / "repo.json").exists():
            print(f"[collector] Skipping existing repo: {owner}/{name}", flush=True)
            continue

        print(f"[collector] Collecting: {owner}/{name}", flush=True)
        collect_repo_raw_data(cfg, repo)
        count += 1

        if args.limit is not None and count >= args.limit:
            print("[collector] Reached limit, stopping.", flush=True)
            break

    print(f"[collector] Finished. Repositories processed: {count}", flush=True)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main(sys.argv[1:]))
