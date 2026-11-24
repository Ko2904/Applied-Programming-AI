"""Small client for the TMDB v3 API used by ScreenScope's film catalogue."""

from __future__ import annotations

from typing import Any

import requests


class TMDBClient:
    """Fetch trending titles and movie details from TMDB."""

    BASE_URL = "https://api.themoviedb.org/3"

    def __init__(
        self,
        read_access_token: str,
        session: requests.Session | None = None,
        timeout: float = 12.0,
    ) -> None:
        if not read_access_token.strip():
            raise ValueError("A TMDB read access token is required.")
        self.session = session or requests.Session()
        self.timeout = timeout
        self.session.headers.update(
            {
                "Authorization": f"Bearer {read_access_token.strip()}",
                "accept": "application/json",
                "User-Agent": "ScreenScope-TV-Explorer/1.0",
            }
        )

    def _get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        response = self.session.get(
            f"{self.BASE_URL}{path}",
            params=params,
            timeout=self.timeout,
        )
        response.raise_for_status()
        return response.json()

    def get_trending(
        self,
        media_type: str,
        time_window: str = "week",
    ) -> list[dict[str, Any]]:
        if media_type not in {"tv", "movie"}:
            raise ValueError("Media type must be 'tv' or 'movie'.")
        if time_window not in {"day", "week"}:
            raise ValueError("Time window must be 'day' or 'week'.")
        data = self._get(f"/trending/{media_type}/{time_window}")
        return data.get("results", [])

    def search_movies(self, query: str) -> list[dict[str, Any]]:
        data = self._get(
            "/search/movie",
            {"query": query, "include_adult": "false"},
        )
        return data.get("results", [])

    def get_movie(self, movie_id: int) -> dict[str, Any]:
        return self._get(
            f"/movie/{movie_id}",
            {"append_to_response": "credits"},
        )


def image_url(file_path: str | None, size: str = "w500") -> str | None:
    """Build a TMDB image URL only from a valid TMDB file path."""
    if not file_path or not file_path.startswith("/"):
        return None
    if not all(character.isalnum() or character in "/._-" for character in file_path):
        return None
    if size not in {"w342", "w500", "w780", "w1280", "original"}:
        raise ValueError("Unsupported TMDB image size.")
    return f"https://image.tmdb.org/t/p/{size}{file_path}"
