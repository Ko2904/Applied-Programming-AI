# ScreenScope — TV and film explorer

## Purpose

ScreenScope is an interactive Streamlit app for exploring TV series, films,
episodes, casts, schedules, and performer credits. It combines TVMaze series
and people information with TMDB trending picks and film details.

## Data collection

The app makes requests to the public [TVMaze REST API](https://www.tvmaze.com/api)
for series search and details, episodes, casts, schedules, people, and
performer credits. It requests trending series, trending films, movie search,
and film details from the [TMDB API](https://developer.themoviedb.com/). TVMaze
features do not require a key. TMDB features require a TMDB Read Access Token.

## Data persistence

The app does not maintain a database or persist a user profile. Streamlit
caches API responses temporarily (30 minutes or one hour, depending on the
request) to reduce repeated network calls. The cache is temporary application
state, not a permanent local data store.

## User interaction

Use the sidebar to navigate between **Discover**, **Daily schedule**, and
**People & credits**. Search and select series or films, explore series
episodes and cast, choose schedule date and country, or search for performers
and inspect their credits. If no TMDB token is configured, TVMaze series
features remain available and the app explains that film and trending
features are unavailable.

## Setup

From this directory, create and activate a virtual environment, install
dependencies, and run the app:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
streamlit run app.py
```

An internet connection is required. To enable TMDB features, create
`.streamlit/secrets.toml`:

```toml
TMDB_READ_ACCESS_TOKEN = "YOUR_TMDB_READ_ACCESS_TOKEN"
```

Alternatively, set the `TMDB_READ_ACCESS_TOKEN` environment variable. The
local secrets file is ignored by Git. For a hosted Streamlit deployment, enter
the value in its Secrets settings. Never commit or publish the token.

Run the API-client tests with `python -m unittest discover -s tests -v`. The
Python dependencies are listed in [`requirements.txt`](./requirements.txt).

## Learning

The project practices REST API clients, request error handling, caching,
interactive Streamlit navigation, and combining data from two services. A key
challenge is supporting useful discovery when the optional TMDB credential is
missing: the app keeps TVMaze-based series features available while presenting
a clear explanation for unavailable film and trending features. The clients
in [`tvmaze_client.py`](./tvmaze_client.py) and [`tmdb_client.py`](./tmdb_client.py)
keep API requests separate from the UI.

## Limitations and assistance

This is a learning project, not an official service from TVMaze or TMDB. It
depends on external API availability, rate limits, terms, and data accuracy.
Trending results can change; film features need a TMDB token; and cached
results are temporary. TVMaze data is licensed under
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/); retain
appropriate attribution and consider its share-alike terms when reusing data.
The app displays TMDB's notice: “This product uses the TMDB API but is not
endorsed or certified by TMDB.” See [TMDB attribution
requirements](https://developer.themoviedb.org/docs/faq). Images belong to
their respective rights holders.

The project uses the third-party Python packages in
[`requirements.txt`](./requirements.txt), along with TVMaze and TMDB APIs.
No externally copied source-code snippets are identified in this project;
dependencies and services are used through their documented interfaces. The
repository's MIT license covers original project code only; see
[the third-party notices](../THIRD_PARTY_NOTICES.md) for content exclusions.
