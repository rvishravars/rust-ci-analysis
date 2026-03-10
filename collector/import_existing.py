"""Legacy import_existing entrypoint.

This helper was used to backfill Postgres from already-downloaded JSON/JSONL
files under ``data/``. The pipeline now runs end-to-end directly from the
collector into Postgres, so this module is intentionally left as a no-op
stub to avoid accidental use.
"""

from __future__ import annotations


def main() -> int:  # pragma: no cover
    raise SystemExit(
        "collector.import_existing is deprecated. "
        "Please run the main collector pipeline instead."
    )


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
