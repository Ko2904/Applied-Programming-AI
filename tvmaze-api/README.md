# ScreenScope — TVMaze API Explorer

An interactive, dark-themed Streamlit app for discovering trending series and
films, then exploring show episodes, cast, schedules, and performer credits.
Series details use the public [TVMaze REST API](https://www.tvmaze.com/api);
trending picks and film details use the [TMDB API](https://developer.themoviedb.org/).

## Run it locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

TVMaze features need no API key. An internet connection is required. TMDB
trending and movie search need a TMDB Read Access Token.

To enable film and trending banners locally, create `.streamlit/secrets.toml`
from the example and add your token:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Set `TMDB_READ_ACCESS_TOKEN` in `.streamlit/secrets.toml` or as an environment
variable. The local secrets file is ignored by Git. For a hosted Streamlit app,
add the same value in the app's Secrets settings; never commit your token.

## Explore

- **Discover** — dark cinematic home screen with weekly TMDB trending series
  and film hero banners, image cards, and separate series/film search.
- **Series details** — TVMaze ratings, genre distribution, seasons, episode
  summaries, and main cast.
- **Film details** — TMDB rating, release date, runtime, overview, and cast.
- **Daily schedule** — browse local TV or streaming schedules by date and
  country; choose all countries for the global streaming schedule.
- **People & credits** — search performers and inspect the shows they appear in.

The request code lives in [`tvmaze_client.py`](./tvmaze_client.py) and
[`tmdb_client.py`](./tmdb_client.py); the UI and cached data functions are in
[`app.py`](./app.py). Responses are cached in Streamlit to keep repeated
interactions quick and limit redundant API calls. Errors from the API are shown
in the app rather than being hidden.

## Learn the API

The app demonstrates these public endpoints:

| App feature | TVMaze endpoint |
| --- | --- |
| Show search | `/search/shows?q=...` |
| People search | `/search/people?q=...` |
| Show details | `/shows/{id}` |
| Episode guide | `/shows/{id}/episodes` |
| Main cast | `/shows/{id}/cast` |
| Local schedule | `/schedule?date=...&country=...` |
| Streaming schedule | `/schedule/web?date=...&country=...` |
| Performer credits | `/people/{id}/castcredits?embed=show` |
| Trending series | TMDB `/3/trending/tv/week` |
| Trending films | TMDB `/3/trending/movie/week` |
| Film search and details | TMDB `/3/search/movie`, `/3/movie/{id}` |

TVMaze documents rate limits and caching in its
[API documentation](https://www.tvmaze.com/api#rate-limiting). TMDB API use
requires attribution; this app displays the required notice: “This product uses
the TMDB API but is not endorsed or certified by TMDB.” See
[TMDB attribution requirements](https://developer.themoviedb.org/docs/faq).
TVMaze data is licensed under
[CC BY-SA](https://creativecommons.org/licenses/by-sa/4.0/); keep attribution
and the license in mind when reusing or redistributing data. Images belong to
their respective rights holders.

## Run the tests

```bash
python -m unittest discover -s tests -v
```
