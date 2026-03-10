from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

import requests


@dataclass
class GitHubClient:
    """Minimal GitHub REST API client for the collector.

    This client focuses on read-only operations and simple rate-limit handling.
    """

    token: str
    base_url: str = "https://api.github.com"

    def _headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github+json",
        }

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Perform a GET request with basic rate-limit awareness.

        On 403 rate-limit responses, waits until reset (up to a bounded delay)
        and retries. Raises for non-success status codes.
        """

        url = f"{self.base_url}{path}"

        while True:
            response = requests.get(url, headers=self._headers(), params=params)

            if response.status_code == 403 and "rate limit" in response.text.lower():
                reset_ts = int(response.headers.get("X-RateLimit-Reset", "0"))
                now = int(time.time())
                wait_seconds = max(0, reset_ts - now + 1)
                # Avoid sleeping for extremely long periods in one go.
                if wait_seconds > 0:
                    time.sleep(min(wait_seconds, 60))
                    continue

            response.raise_for_status()
            return response

    def search_repositories(
        self,
        query: str,
        *,
        sort: Optional[str] = "stars",
        order: str = "desc",
        per_page: int = 100,
    ) -> Iterable[Dict[str, Any]]:
        """Yield repositories matching the given search query.

        GitHub caps search results at 1,000 items; this method respects that
        by stopping after the cap is reached or when a page returns fewer
        than `per_page` results.
        """

        page = 1
        while True:
            params = {
                "q": query,
                "sort": sort,
                "order": order,
                "per_page": per_page,
                "page": page,
            }
            response = self.get("/search/repositories", params=params)
            payload = response.json()
            items = payload.get("items", []) or []

            if not items:
                break

            for item in items:
                yield item

            if len(items) < per_page:
                break

            page += 1
            if page * per_page > 1000:
                # GitHub search API does not return more than 1,000 results.
                break
