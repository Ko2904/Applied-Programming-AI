"""Small, testable client for the public TVMaze REST API."""

from __future__ import annotations

from typing import Any

import requests


class TVMazeClient:
    """Make JSON requests to TVMaze without hiding HTTP or decoding errors."""

    BASE_URL = "https://api.tvmaze.com"

    def __init__(
        self,
        session: requests.Session | None = None,
        timeout: float = 12.0,
    ) -> None:
        self.session = session or requests.Session()
        self.timeout = timeout
        self.session.headers.update({"User-Agent": "ScreenScope-TV-Explorer/1.0"})

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        response = self.session.get(
            f"{self.BASE_URL}{path}",
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def search_shows(self, query: str) -> list[dict[str, Any]]:
        return self._get("/search/shows", {"q": query})

    def search_people(self, query: str) -> list[dict[str, Any]]:
        return self._get("/search/people", {"q": query})

    def get_show(self, show_id: int) -> dict[str, Any]:
        return self._get(f"/shows/{show_id}")

    def get_episodes(
        self,
        show_id: int,
        include_specials: bool = False,
    ) -> list[dict[str, Any]]:
        params = {"specials": 1} if include_specials else None
        return self._get(f"/shows/{show_id}/episodes", params)

    def get_cast(self, show_id: int) -> list[dict[str, Any]]:
        return self._get(f"/shows/{show_id}/cast")

    def get_schedule(
        self,
        date: str,
        country: str = "US",
        streaming: bool = False,
    ) -> list[dict[str, Any]]:
        endpoint = "/schedule/web" if streaming else "/schedule"
        params: dict[str, str] = {"date": date, "country": country}
        return self._get(endpoint, params)

    def search_person_cast_credits(
        self,
        person_id: int,
    ) -> list[dict[str, Any]]:
        return self._get(
            f"/people/{person_id}/castcredits",
            {"embed": "show"},
        )
