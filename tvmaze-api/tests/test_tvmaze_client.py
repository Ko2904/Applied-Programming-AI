import unittest
from unittest.mock import Mock

import requests

from tvmaze_client import TVMazeClient


class TVMazeClientTests(unittest.TestCase):
    def setUp(self) -> None:
        self.session = Mock(spec=requests.Session)
        self.session.headers = {}
        self.client = TVMazeClient(session=self.session)

    def test_search_shows_uses_documented_search_endpoint(self) -> None:
        response = Mock()
        response.json.return_value = [{"show": {"id": 42, "name": "Example"}}]
        self.session.get.return_value = response

        result = self.client.search_shows("Example")

        self.assertEqual(result[0]["show"]["id"], 42)
        self.session.get.assert_called_once_with(
            "https://api.tvmaze.com/search/shows",
            params={"q": "Example"},
            timeout=12.0,
        )
        response.raise_for_status.assert_called_once_with()

    def test_global_streaming_schedule_uses_empty_country(self) -> None:
        response = Mock()
        response.json.return_value = []
        self.session.get.return_value = response

        self.client.get_schedule("2025-01-02", country="", streaming=True)

        self.session.get.assert_called_once_with(
            "https://api.tvmaze.com/schedule/web",
            params={"date": "2025-01-02", "country": ""},
            timeout=12.0,
        )

    def test_http_errors_are_not_silently_converted_to_empty_results(self) -> None:
        response = Mock()
        response.raise_for_status.side_effect = requests.HTTPError("Not found")
        self.session.get.return_value = response

        with self.assertRaises(requests.HTTPError):
            self.client.get_show(404)


if __name__ == "__main__":
    unittest.main()
