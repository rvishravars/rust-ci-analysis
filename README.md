# Rust CI Renewed

This repository accompanies the paper *An Empirical Study of Continuous Integration in Open-Source Rust Projects*. It contains:

- A summary of all metrics extracted from the paper in [metrics.md](metrics.md).
- A Python "collector" that can re-gather the repository list and raw data needed for later analytics.
- Docker support to run the collector in a containerized environment.

## Contents

- [Rust_CI_for_Publication.pdf](Rust_CI_for_Publication.pdf) 
- [metrics.md](metrics.md) – human-readable list of all reported metrics and a checklist-style implementation plan.
- [collector/](collector) – Python package for data collection:
  - [collector/config.py](collector/config.py) – environment-driven configuration (search parameters, storage paths, GitHub token).
  - [collector/github_client.py](collector/github_client.py) – minimal GitHub REST client with pagination and simple rate-limit handling.
  - [collector/repo_discovery.py](collector/repo_discovery.py) – discovers Rust repositories via the GitHub API and writes a JSONL repo list.
  - [collector/repo_data.py](collector/repo_data.py) – downloads raw per-repo data (repo metadata, languages, commits, issues, workflows, workflow runs).
  - [collector/__main__.py](collector/__main__.py) – CLI entry point (`python -m collector`).
- [requirements.txt](requirements.txt) – Python dependencies.
- [Dockerfile](Dockerfile) and [.dockerignore](.dockerignore) – container image for running the collector.

## Prerequisites

- Docker and Docker Compose.
- A GitHub personal access token with read-only access to public repositories.

Configure your environment variables via [.env](.env):

- `GITHUB_TOKEN` (required)
- Optional filters and paths, for example:
  - `RUST_CI_DATA_DIR` – base directory for collected data (default: `./data`).
  - `RUST_CI_MIN_STARS`, `RUST_CI_MIN_FORKS`.
  - `RUST_CI_CREATED_FROM`, `RUST_CI_CREATED_TO`.
  - `RUST_CI_MONOGLOT_ONLY`, `RUST_CI_POLYGLOT_ONLY` (currently interpreted at analysis time, not encoded in the search query).

> Important: do **not** commit real tokens to version control.

## Running the Collector with Docker Compose

1. Build the image:

   ```bash
   docker compose build collector
   ```

2. Ensure you have a data directory on the host (Compose mounts `./data` to `/data` in the container):

   ```bash
   mkdir -p data
   ```

3. Run the collector with your `.env` file and volume mount:

   ```bash
   docker compose run --rm collector --limit 10 --resume
   ```

This will:

- Discover Rust repositories using the configured search parameters.
- Write a JSONL repo list to `/data/repos.jsonl` in the container (mapped to `./data/repos.jsonl` on the host).
- For each repository, download and store raw JSON/JSONL under `/data/raw/github/<owner>/<repo>/` (mapped under `./data/raw/...`).

## What Gets Collected (Raw Only)

For each repository, the collector stores **raw** data only (no analysis):

- `repo.json` – basic repo metadata (IDs, names, counts, timestamps).
- `languages.json` – language breakdown from the GitHub languages API.
- `commits.jsonl` – paginated commit history.
- `issues.jsonl` – all issues and pull requests (state=all).
- `workflows.json` – GitHub Actions workflow definitions.
- `workflow_runs.jsonl` – CI run metadata for later build/coverage analysis.

These files are intended to be consumed by separate analysis scripts or notebooks (not included here yet).

## Next Steps

- Implement analysis scripts / notebooks that read the collected raw data and reproduce or extend the metrics summarized in [metrics.md](metrics.md).
- Add tests and a simple manifest file as outlined in the plan section at the bottom of [metrics.md](metrics.md).
