import unittest
from unittest.mock import Mock

import requests

from tmdb_client import TMDBClient, image_url


class TMDBClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = Mock(spec=requests.Session)
        self.session.headers = {}
        self.client = TMDBClient("test-read-token", session=self.session)

    def test_trending_movie_request_uses_bearer_auth(self) -> None:
        response = Mock()
        response.json.return_value = {"results": [{"id": 12, "title": "Example"}]}
        self.session.get.return_value = response

        result = self.client.get_trending("movie")

        self.assertEqual(result[0]["id"], 12)
        self.assertEqual(
            self.session.headers["Authorization"],
            "Bearer test-read-token",
        )
        self.session.get.assert_called_once_with(
            "https://api.themoviedb.org/3/trending/movie/week",
            params=None,
            timeout=12.0,
        )
        response.raise_for_status.assert_called_once_with()

    def test_invalid_trending_category_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.client.get_trending("person")

    def test_movie_details_request_includes_credits(self) -> None:
        response = Mock()
        response.json.return_value = {"id": 7, "credits": {"cast": []}}
        self.session.get.return_value = response

        result = self.client.get_movie(7)

        self.assertEqual(result["id"], 7)
        self.session.get.assert_called_once_with(
            "https://api.themoviedb.org/3/movie/7",
            params={"append_to_response": "credits"},
            timeout=12.0,
        )

    def test_image_url_rejects_non_path_input(self) -> None:
        self.assertEqual(
            image_url("/abc.jpg"),
            "https://image.tmdb.org/t/p/w500/abc.jpg",
        )
        self.assertIsNone(image_url("https://example.com/image.jpg"))
        self.assertIsNone(image_url("/image.jpg?unsafe=true"))


if __name__ == "__main__":
    unittest.main()
