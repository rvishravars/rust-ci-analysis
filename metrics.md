# Metrics Extracted from "An Empirical Study of Continuous Integration in Open-Source Rust Projects"

## Dataset and Project-Level Metrics

- Total projects analyzed: 2,256 open-source Rust projects on GitHub.
- Cohorts:
  - Monoglot (pure Rust) projects.
  - Polyglot (Rust plus other languages) projects.
- Project size categories (used across tables/figures): small, medium, large.

## Commit Frequency / Development Activity

- Commit frequency metric: commits per weekday.
- Table 1 (Commit Frequency Statistics by Cohort and Project):
  - Commit frequency by cohort (monoglot vs polyglot) and project size (small/medium/large), including:
    - Mean commits per weekday.
    - Median (implied via distribution discussion and figures).
    - Distribution across cohorts and sizes (visualized in Figure 2).
- Key reported values (from text):
  - Median commit rate for large polyglot projects: 6.96 commits per weekday.
  - Median commit rate for large monoglot projects: 1.20 commits per weekday.

## Broken Build Durations

- Metric: duration of broken build stretches (days) on the main branch.
- Table 2 (Statistics of broken build durations (days) by cohort and project size):
  - For each cohort (monoglot, polyglot) and size (small, medium, large):
    - Mean duration of broken builds (days).
    - Count of broken-build stretches.
    - Standard deviation of broken-build duration.
- Key reported values (from text):
  - Monoglot small projects:
    - Mean broken build duration: 27.39 days.
    - Median broken build duration: 0.55 days.
  - Monoglot medium and large projects: reduced mean and median broken build durations compared to small projects (exact medians referenced qualitatively).

## Build Duration

- Metric: CI build duration (minutes).
- Table 3 (Build duration statistics (minutes) by cohort and project size):
  - For each cohort (monoglot, polyglot) and size (small, medium, large):
    - Mean build time (minutes).
    - Median build time (minutes).
    - First quartile (Q1) build time (minutes).
    - Third quartile (Q3) build time (minutes).
- Key reported values (from text):
  - Small projects (both cohorts): mean build times around 5.5 minutes.
  - Large polyglot projects: mean build time approximately 11.2 minutes.
  - Some large polyglot projects: build times exceeding 15 minutes.

## Test Coverage Levels

- Metric: line/function test coverage percentage reported by CI (0–100%).
- Table 4 (Test coverage statistics by cohort):
  - Coverage statistics for projects with configured and non-zero coverage, by cohort:
    - Monoglot projects:
      - Mean coverage: 87.79%.
      - Q1 coverage: 76.50%.
      - Q3 coverage: 100.00%.
    - Polyglot projects:
      - Mean coverage: 78.12%.
      - Q1 coverage: 69.80%.
      - Q3 coverage: 96.44%.
- Coverage adoption metrics:
  - Projects with CI tests:
    - 462 monoglot projects.
    - 1,093 polyglot projects.
  - Projects with configured, non-zero coverage:
    - 3.05% of monoglot projects.
    - 5.05% of polyglot projects.
  - Projects without actionable coverage data:
    - 540 monoglot projects.
    - 1,334 polyglot projects.

## CI Adoption Time

- Metric: time from project creation to first CI adoption (months).
- Table 5 (CI adoption time statistics by cohort and project size):
  - For each cohort (monoglot, polyglot) and size (small, medium, large):
    - Mean time to first CI (months).
    - First quartile (Q1) time to first CI (months).
    - Third quartile (Q3) time to first CI (months).
- Reported values:
  - Monoglot projects:
    - Small: mean 63.64 months; Q1 39.00; Q3 87.00.
    - Medium: mean 66.01 months; Q1 39.75; Q3 94.25.
    - Large: mean 56.67 months; Q1 46.75; Q3 67.25.
  - Polyglot projects:
    - Small: mean 49.05 months; Q1 23.00; Q3 71.00.
    - Medium: mean 49.82 months; Q1 22.50; Q3 70.50.
    - Large: mean 47.63 months; Q1 24.00; Q3 69.00.
- Additional comparative metric (from discussion):
  - In general open-source projects (Hilton et al.), median time to adopt CI: about 1 year (~12 months) after project inception.

## Development Velocity (Pre-CI)

- Metric: development velocity measured as commits per weekday in the period leading up to CI adoption.
- Table 6 (Development velocity and time to first CI adoption statistics by cohort):
  - For each cohort (monoglot, polyglot):
    - Velocity statistics (commits per weekday):
      - Mean.
      - Standard deviation.
      - 25th percentile (Q1).
      - 50th percentile (median).
      - 75th percentile (Q3).
      - Maximum.
    - Time to first CI adoption statistics (months):
      - Mean.
      - Standard deviation.
      - 25th percentile (Q1).
      - 50th percentile (median).
      - 75th percentile (Q3).
      - Maximum.
- Reported values (velocity):
  - Monoglot:
    - Mean velocity: 2.02 commits per weekday.
    - Standard deviation: 6.95.
    - Q1: 0.12 commits per weekday.
    - Median: 0.58 commits per weekday.
    - Q3: 1.96 commits per weekday.
    - Maximum: 130.92 commits per weekday.
  - Polyglot:
    - Mean velocity: 8.61 commits per weekday.
    - Standard deviation: 26.06.
    - Q1: 0.38 commits per weekday.
    - Median: 2.27 commits per weekday.
    - Q3: 7.54 commits per weekday.
    - Maximum: 757.38 commits per weekday.
- Reported values (time to CI, duplicating metrics in Table 5 but summarized at cohort level):
  - Monoglot:
    - Mean time to first CI adoption: 64.33 months.
    - Standard deviation: 34.25 months.
    - Q1: 39.50 months.
    - Median: 62.00 months.
    - Q3: 90.50 months.
    - Maximum: 156.00 months.
  - Polyglot:
    - Mean time to first CI adoption: 49.23 months.
    - Standard deviation: 33.31 months.
    - Q1: 23.00 months.
    - Median: 46.00 months.
    - Q3: 70.00 months.
    - Maximum: 162.00 months.

## Defect / Bug Issue Metrics

- Metric: number of bug-like issues reported, comparing pre-CI and post-CI periods.
- Figure 9 (Bug issues count before and after CI adoption, by project cohort):
  - Visual distribution of bug issue counts for monoglot vs polyglot projects, before and after CI adoption.
- Table 7 (Statistics for bug issues before and after CI adoption by cohort):
  - Monoglot projects:
    - Bug issues before CI:
      - Mean: 68.21 issues.
      - Q1: 15.5 issues.
      - Q3: 81.00 issues.
    - Bug issues after CI:
      - Mean: 12.23 issues.
      - Q1: 1.0 issue.
      - Q3: 14.00 issues.
  - Polyglot projects:
    - Bug issues before CI:
      - Mean: 170.60 issues.
      - Q1: 18.0 issues.
      - Q3: 163.00 issues.
    - Bug issues after CI:
      - Mean: 72.99 issues.
      - Q1: 4.0 issues.
      - Q3: 48.25 issues.
- Summary insight (from text):
  - CI adoption correlates with a significant reduction in reported bug-like issues across both monoglot and polyglot Rust projects.

## CI Test and Coverage Adoption Metrics

- Presence of CI tests:
  - Number of monoglot projects with CI tests: 462.
  - Number of polyglot projects with CI tests: 1,093.
- Coverage adoption (subset with configured, non-zero coverage):
  - Monoglot: 3.05% of projects.
  - Polyglot: 5.05% of projects.
- Projects without actionable coverage data:
  - Monoglot: 540 projects.
  - Polyglot: 1,334 projects.

## Co-language Usage (Descriptive Metrics)

- Figure 1 (Top co-language usage in Rust-majority and Rust-minority projects):
  - Shows distribution of commonly co-used languages (e.g., C, C++, Python, JavaScript) with Rust.
  - While specific numeric values are visual, the metric captured is the frequency of each co-language appearing alongside Rust in projects, split by Rust-majority vs Rust-minority repositories.

## Overview of CI Theater-Related Metrics

Across the study, the following families of metrics are used to identify potential CI Theater anti-patterns in Rust projects:

- Commit frequency (commits per weekday) by cohort and size.
- Duration of broken build stretches (days) by cohort and size.
- CI build durations (minutes) by cohort and size.
- Test coverage percentages for projects with configured coverage.
- Adoption rates of CI tests and coverage instrumentation.
- Time from project creation to first CI adoption (months).
- Development velocity (pre-CI) in commits per weekday.
- Bug issue counts before vs after CI adoption.
- Co-language usage frequencies for Rust-majority and Rust-minority projects.

## Plan: Python Pipeline to Regather Repos and Raw Data

- [x] Define configuration
  - [x] Capture search parameters (language=Rust, stars/forks thresholds, time window, monoglot vs polyglot flags).
  - [x] Specify input/output locations (e.g., repos list CSV/JSON, raw data directory structure).
  - [x] Store GitHub/Forge API tokens securely via environment variables.
- [x] Implement repository discovery
  - [x] Write a Python module to query the GitHub API for Rust projects using the same criteria as the paper.
  - [x] Implement pagination and rate limiting / backoff handling.
  - [x] Persist the resulting repository list (ID, full_name, default_branch, language breakdown, metadata) to disk.
- [x] Implement data collection per repository
  - [x] For each repo in the list, download and cache:
    - [x] Basic repository metadata (languages, topics, default branch, creation date).
    - [x] Commit history needed for velocity/CI-adoption metrics (timestamps, authors, commit messages).
    - [x] CI configuration files (e.g., GitHub Actions workflows, other CI configs) for later parsing.
    - [x] Issue and label data for bug/defect metrics (issue state, creation/close times, labels).
  - [x] Save each repo’s raw data in a reproducible directory layout (e.g., data/raw/<platform>/<owner>/<repo>/...).
- [ ] Implement CI signal extraction (raw only)
  - [ ] Collect raw CI run/build logs or job metadata where available (e.g., workflow runs, statuses, durations).
  - [ ] Capture raw test-coverage artifacts/values if exposed by the CI provider.
  - [ ] Store CI-related responses without transforming them (JSON dumps or ndjson).
- [x] Add orchestration script
  - [x] Implement a command-line entry point (e.g., python -m rust_ci_scraper) that:
    - [x] Loads configuration and repo list (or regenerates it if missing/stale).
    - [x] Iterates over repositories and triggers the data collection routines with resume/restart support.
    - [x] Logs progress and errors to a simple log file for later debugging (stdout for now).
- [ ] Hardening and reproducibility
  - [ ] Add minimal tests for API client and file layout helpers (no analytics logic).
  - [ ] Document usage in a README section (prerequisites, environment variables, how to run the collector).
  - [ ] Add a simple manifest file summarizing collection date, query parameters, and counts of repos/objects fetched.
