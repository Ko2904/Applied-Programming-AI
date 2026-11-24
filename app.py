from __future__ import annotations

import os
import re
from collections import Counter
from datetime import date
from html import escape, unescape
from pathlib import Path
from typing import Any

import requests
import streamlit as st

from tmdb_client import TMDBClient, image_url as tmdb_image_url
from tvmaze_client import TVMazeClient


st.set_page_config(
    page_title="ScreenScope | TVMaze Explorer",
    page_icon="📺",
    layout="wide",
    initial_sidebar_state="expanded",
)

API = TVMazeClient()
TMDB_NOTICE = (
    "This product uses the TMDB API but is not endorsed or certified by TMDB."
)
TMDB_GENRES = {
    12: "Adventure",
    14: "Fantasy",
    16: "Animation",
    18: "Drama",
    27: "Horror",
    28: "Action",
    35: "Comedy",
    36: "History",
    37: "Western",
    53: "Thriller",
    80: "Crime",
    99: "Documentary",
    878: "Sci-Fi",
    9648: "Mystery",
    10749: "Romance",
    10751: "Family",
    10752: "War",
    10759: "Action & Adventure",
    10762: "Kids",
    10763: "News",
    10764: "Reality",
    10765: "Sci-Fi & Fantasy",
    10766: "Soap",
    10767: "Talk",
    10768: "War & Politics",
    10770: "TV Movie",
    10402: "Music",
}


def tmdb_client() -> TMDBClient | None:
    token = os.environ.get("TMDB_READ_ACCESS_TOKEN", "").strip()
    secret_files = (
        Path(__file__).parent / ".streamlit" / "secrets.toml",
        Path.home() / ".streamlit" / "secrets.toml",
    )
    if not token and any(secret_file.is_file() for secret_file in secret_files):
        token = str(st.secrets.get("TMDB_READ_ACCESS_TOKEN", "")).strip()
    return TMDBClient(token) if token else None


@st.cache_data(ttl=3600, show_spinner=False)
def search_shows(query: str) -> list[dict[str, Any]]:
    return API.search_shows(query)


@st.cache_data(ttl=3600, show_spinner=False)
def search_people(query: str) -> list[dict[str, Any]]:
    return API.search_people(query)


@st.cache_data(ttl=3600, show_spinner=False)
def get_show(show_id: int) -> dict[str, Any]:
    return API.get_show(show_id)


@st.cache_data(ttl=3600, show_spinner=False)
def get_episodes(show_id: int, include_specials: bool) -> list[dict[str, Any]]:
    return API.get_episodes(show_id, include_specials)


@st.cache_data(ttl=3600, show_spinner=False)
def get_cast(show_id: int) -> list[dict[str, Any]]:
    return API.get_cast(show_id)


@st.cache_data(ttl=3600, show_spinner=False)
def get_schedule(
    selected_date: str,
    country: str,
    streaming: bool,
) -> list[dict[str, Any]]:
    return API.get_schedule(selected_date, country, streaming)


@st.cache_data(ttl=3600, show_spinner=False)
def get_person_credits(person_id: int) -> list[dict[str, Any]]:
    return API.search_person_cast_credits(person_id)


@st.cache_data(ttl=1800, show_spinner=False)
def get_trending(media_type: str) -> list[dict[str, Any]]:
    client = tmdb_client()
    if client is None:
        return []
    return client.get_trending(media_type, "week")


@st.cache_data(ttl=1800, show_spinner=False)
def search_movies(query: str) -> list[dict[str, Any]]:
    client = tmdb_client()
    if client is None:
        return []
    return client.search_movies(query)


@st.cache_data(ttl=1800, show_spinner=False)
def get_movie(movie_id: int) -> dict[str, Any]:
    client = tmdb_client()
    if client is None:
        raise RuntimeError("TMDB is not configured.")
    return client.get_movie(movie_id)


@st.cache_data(ttl=3600, show_spinner=False)
def get_featured_series() -> list[dict[str, Any]]:
    featured_queries = (
        "Severance",
        "Breaking Bad",
        "The Bear",
        "Stranger Things",
        "Game of Thrones",
        "The Office",
    )
    shows: dict[int, dict[str, Any]] = {}
    for query in featured_queries:
        results = API.search_shows(query)
        if results and results[0].get("show"):
            show = results[0]["show"]
            shows[show["id"]] = show
    return sorted(
        shows.values(),
        key=lambda show: (
            (show.get("rating") or {}).get("average") or 0,
            show.get("weight") or 0,
        ),
        reverse=True,
    )


def plain_text(markup: str | None) -> str:
    if not markup:
        return ""
    with_line_breaks = re.sub(r"</(?:p|li|br)\s*>", "\n", markup, flags=re.I)
    return unescape(re.sub(r"<[^>]*>", "", with_line_breaks)).strip()


def show_rating(show: dict[str, Any]) -> str:
    rating = (show.get("rating") or {}).get("average")
    return f"{rating:.1f}" if isinstance(rating, (int, float)) else "N/A"


def apply_visual_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            color-scheme: dark;
            --screen-bg: #090b10;
            --screen-panel: #11151d;
            --screen-line: rgba(255,255,255,.09);
            --screen-text: #f5f6f8;
            --screen-muted: #9da5b3;
            --screen-accent: #d3f36b;
        }
        .stApp {
            background:
                radial-gradient(ellipse at 70% -20%, rgba(76,92,113,.16), transparent 42%),
                var(--screen-bg);
            color: var(--screen-text);
        }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stSidebar"] {
            background: #0c0f15;
            border-right: 1px solid var(--screen-line);
        }
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
            color: var(--screen-muted);
        }
        .block-container { max-width: 1440px; padding-top: 2rem; }
        h1, h2, h3 { letter-spacing: -.035em; }
        h1 { font-weight: 720; }
        .screen-kicker {
            color: var(--screen-accent);
            font-size: .72rem;
            font-weight: 750;
            letter-spacing: .16em;
            text-transform: uppercase;
            margin-bottom: .45rem;
        }
        .screen-subtitle { color: var(--screen-muted); margin-top: -.5rem; }
        .screen-section-title {
            display: flex;
            align-items: baseline;
            justify-content: space-between;
            gap: 1rem;
            margin: 2.2rem 0 1rem;
        }
        .screen-section-title h2 { margin: 0; font-size: 1.45rem; }
        .screen-section-title span { color: var(--screen-muted); font-size: .85rem; }
        .screen-hero {
            position: relative;
            min-height: 340px;
            display: flex;
            align-items: flex-end;
            padding: clamp(1.5rem, 4vw, 3.25rem);
            border: 1px solid var(--screen-line);
            border-radius: 22px;
            overflow: hidden;
            background-color: #171d28;
            box-shadow: 0 24px 70px rgba(0,0,0,.25);
        }
        .screen-hero-image {
            position: absolute;
            inset: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            object-position: center 32%;
            opacity: .7;
        }
        .screen-hero-scrim {
            position: absolute;
            inset: 0;
            background: linear-gradient(90deg, rgba(8,10,14,.96) 0%, rgba(8,10,14,.78) 48%, rgba(8,10,14,.2) 100%);
        }
        .screen-hero-content { position: relative; z-index: 1; max-width: 650px; }
        .screen-hero h2 {
            font-size: clamp(2.2rem, 5vw, 4rem);
            line-height: 1.02;
            margin: .35rem 0 .7rem;
            color: white;
        }
        .screen-hero p { color: #d1d5dd; line-height: 1.6; max-width: 60ch; }
        .screen-meta {
            color: #e6e9ef;
            font-size: .83rem;
            font-weight: 600;
            letter-spacing: .02em;
        }
        [data-testid="stTextInput"] input,
        [data-testid="stSelectbox"] [role="combobox"] {
            background-color: #11151d;
            border-color: var(--screen-line);
            border-radius: 10px;
        }
        [data-testid="stButton"] button,
        [data-testid="stFormSubmitButton"] button {
            border-radius: 10px;
            font-weight: 650;
            transition: transform .15s ease, border-color .15s ease;
        }
        [data-testid="stButton"] button:hover,
        [data-testid="stFormSubmitButton"] button:hover {
            transform: translateY(-1px);
            border-color: var(--screen-accent);
        }
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: linear-gradient(160deg, rgba(255,255,255,.025), rgba(255,255,255,.008));
            border-color: var(--screen-line);
            border-radius: 14px;
        }
        [data-testid="stMetric"] {
            background: var(--screen-panel);
            padding: 1rem;
            border: 1px solid var(--screen-line);
            border-radius: 12px;
        }
        [data-testid="stCaptionContainer"] { color: var(--screen-muted); }
        a { color: var(--screen-accent) !important; }
        @media (max-width: 700px) {
            .block-container { padding: 1.2rem 1rem 2rem; }
            .screen-hero { min-height: 300px; border-radius: 16px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def section_heading(title: str, subtitle: str = "") -> None:
    st.markdown(
        f'<div class="screen-section-title"><h2>{escape(title)}</h2>'
        f'<span>{escape(subtitle)}</span></div>',
        unsafe_allow_html=True,
    )


def render_image_hero(
    title: str,
    metadata: str,
    overview: str,
    label: str,
    image: str | None,
) -> None:
    image_markup = (
        f'<img class="screen-hero-image" src="{escape(image, quote=True)}" alt="">'
        if image
        else ""
    )
    st.markdown(
        f"""
        <section class="screen-hero" aria-label="{escape(label, quote=True)}">
          {image_markup}
          <div class="screen-hero-scrim"></div>
          <div class="screen-hero-content">
            <div class="screen-kicker">{escape(label)}</div>
            <h2>{escape(title)}</h2>
            <div class="screen-meta">{escape(metadata)}</div>
            <p>{escape(overview)}</p>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_hero(item: dict[str, Any], media_type: str, label: str) -> None:
    is_movie = media_type == "movie"
    title = item.get("title" if is_movie else "name") or "Untitled"
    date_text = item.get("release_date" if is_movie else "first_air_date") or ""
    year = date_text[:4] or "Year unknown"
    rating = item.get("vote_average")
    rating_text = f"★ {rating:.1f}" if isinstance(rating, (int, float)) else "Unrated"
    genres = [
        TMDB_GENRES[genre_id]
        for genre_id in item.get("genre_ids", [])
        if genre_id in TMDB_GENRES
    ]
    metadata = " · ".join([year, rating_text, *genres[:2]])
    overview = item.get("overview") or "Discover the story, cast, and more."
    overview = overview[:260] + ("…" if len(overview) > 260 else "")
    backdrop = tmdb_image_url(item.get("backdrop_path"), "w1280")
    render_image_hero(title, metadata, overview, label, backdrop)


def render_tvmaze_hero(show: dict[str, Any]) -> None:
    image = (show.get("image") or {}).get("original") or (show.get("image") or {}).get("medium")
    overview = plain_text(show.get("summary")) or "Explore this series on ScreenScope."
    overview = overview[:260] + ("…" if len(overview) > 260 else "")
    genres = " · ".join(show.get("genres") or [])
    premiered = (show.get("premiered") or "")[:4]
    metadata = " · ".join(
        value for value in (premiered, f"★ {show_rating(show)}", genres) if value
    )
    render_image_hero(
        show.get("name", "Untitled"),
        metadata,
        overview,
        "Featured series · TVMaze",
        image,
    )
    if st.button("Explore this series", key=f"featured-tvmaze-{show['id']}", type="primary"):
        st.session_state["selected_movie_id"] = None
        st.session_state["selected_show_id"] = show["id"]
        st.session_state["discover_media_type"] = "Series"
        st.session_state["from_home"] = True
        st.session_state["show_results"] = [{"show": show}]
        st.session_state["show_results_query"] = show.get("name", "")
        st.rerun()


def open_tmdb_series(title: str) -> None:
    try:
        results = search_shows(title)
    except (requests.RequestException, ValueError) as error:
        st.error(f"Could not open this series from TVMaze: {error}")
        return
    if not results or not results[0].get("show"):
        st.info("TVMaze does not have a matching show for this title yet.")
        return
    st.session_state["selected_movie_id"] = None
    st.session_state["selected_show_id"] = results[0]["show"]["id"]
    st.session_state["discover_media_type"] = "Series"
    st.session_state["show_results"] = results
    st.session_state["show_results_query"] = title
    st.session_state["from_home"] = True
    st.rerun()


def render_media_row(items: list[dict[str, Any]], media_type: str) -> None:
    if not items:
        st.caption("No titles are available right now.")
        return
    visible_items = items[:5]
    columns = st.columns(len(visible_items))
    for index, item in enumerate(visible_items):
        title = item.get("title" if media_type == "movie" else "name") or "Untitled"
        poster = tmdb_image_url(item.get("poster_path"), "w500")
        date_text = item.get("release_date" if media_type == "movie" else "first_air_date") or ""
        year = date_text[:4] or "—"
        rating = item.get("vote_average")
        rating_text = f"★ {rating:.1f}" if isinstance(rating, (int, float)) else "Unrated"
        with columns[index]:
            with st.container(border=True):
                if poster:
                    st.image(poster, use_container_width=True)
                else:
                    st.markdown("### 🎬")
                st.markdown(f"**{escape(title)}**")
                st.caption(f"{year} · {rating_text}")
                if media_type == "movie":
                    if st.button(
                        "View film",
                        key=f"movie-card-{item['id']}",
                        use_container_width=True,
                    ):
                        st.session_state["selected_show_id"] = None
                        st.session_state["selected_movie_id"] = item["id"]
                        st.rerun()
                elif st.button(
                    "Explore series",
                    key=f"tv-card-{item['id']}",
                    use_container_width=True,
                ):
                    open_tmdb_series(title)


def show_movie_detail(movie_id: int) -> None:
    try:
        with st.spinner("Loading film details and cast from TMDB…"):
            movie = get_movie(movie_id)
    except (requests.RequestException, RuntimeError, ValueError) as error:
        st.error(f"Could not load this film from TMDB: {error}")
        return
    if st.button("← Back to discovery"):
        st.session_state["selected_movie_id"] = None
        st.rerun()
    st.divider()
    backdrop = tmdb_image_url(movie.get("backdrop_path"), "w1280")
    poster = tmdb_image_url(movie.get("poster_path"), "w500")
    if backdrop:
        st.image(backdrop, use_container_width=True)
    left, right = st.columns([1, 3])
    with left:
        if poster:
            st.image(poster, use_container_width=True)
    with right:
        st.markdown(f"## {movie.get('title') or 'Untitled'}")
        genres = " · ".join(
            genre.get("name", "")
            for genre in movie.get("genres", [])
            if genre.get("name")
        )
        st.caption(
            f"{genres or 'Genres not listed'}  |  "
            f"{(movie.get('release_date') or '—')[:4]}  |  "
            f"{movie.get('status') or 'Status unknown'}"
        )
        metrics = st.columns(3)
        rating = movie.get("vote_average")
        metrics[0].metric(
            "TMDB rating",
            f"{rating:.1f} / 10" if isinstance(rating, (int, float)) else "N/A",
        )
        runtime = movie.get("runtime")
        metrics[1].metric("Runtime", f"{runtime} min" if runtime else "—")
        metrics[2].metric("Votes", movie.get("vote_count") or "—")
        if movie.get("overview"):
            st.write(movie["overview"])
        cast = (movie.get("credits") or {}).get("cast") or []
        if cast:
            st.markdown("### Cast")
            st.write(" · ".join(member.get("name", "") for member in cast[:8]))
        if movie.get("id"):
            st.link_button(
                "Open on TMDB",
                f"https://www.themoviedb.org/movie/{movie['id']}",
            )


def show_search_results(results: list[dict[str, Any]]) -> None:
    if not results:
        st.info("No matches yet. Try another title or a shorter search.")
        return

    shows = [item["show"] for item in results if item.get("show")]
    genre_counts = Counter(
        genre for show in shows for genre in show.get("genres", [])
    )
    if genre_counts:
        st.markdown("#### What’s in these results?")
        st.bar_chart(
            {
                "Shows": dict(genre_counts.most_common(8)),
            },
            height=190,
        )

    st.markdown(f"#### {len(shows)} matching shows")
    columns = st.columns(2)
    for index, show in enumerate(shows):
        with columns[index % 2]:
            with st.container(border=True):
                image = (show.get("image") or {}).get("medium")
                poster_col, info_col = st.columns([1, 2.4])
                with poster_col:
                    if image:
                        st.image(image, use_container_width=True)
                    else:
                        st.markdown("### 🎬")
                with info_col:
                    st.markdown(f"### {show.get('name', 'Untitled')}")
                    genres = " · ".join(show.get("genres") or []) or "Genre unknown"
                    year = (show.get("premiered") or "—")[:4]
                    st.caption(f"{genres}  \n{year} · {show.get('status', 'Unknown')}")
                    st.markdown(f"**Rating:** {show_rating(show)} / 10")
                    if st.button(
                        "Open show",
                        key=f"open-show-{show['id']}",
                        use_container_width=True,
                    ):
                        st.session_state["selected_show_id"] = show["id"]
                        st.rerun()


def show_detail(show_id: int) -> None:
    try:
        with st.spinner("Loading show, episode guide, and cast from TVMaze…"):
            show = get_show(show_id)
            episodes = get_episodes(show_id, include_specials=True)
            cast = get_cast(show_id)
    except (requests.RequestException, ValueError) as error:
        st.error(f"Could not load this show from TVMaze: {error}")
        return

    back_label = (
        "← Back to discovery"
        if st.session_state.get("from_home")
        else "← Back to series search"
    )
    if st.button(back_label):
        st.session_state["selected_show_id"] = None
        if st.session_state.get("from_home"):
            st.session_state.pop("show_results", None)
            st.session_state.pop("from_home", None)
        st.rerun()

    st.divider()
    poster, overview = st.columns([1, 3])
    image = (show.get("image") or {}).get("original") or (show.get("image") or {}).get("medium")
    with poster:
        if image:
            st.image(image, use_container_width=True)
    with overview:
        st.markdown(f"## {show.get('name', 'Untitled')}")
        genres = " · ".join(show.get("genres") or []) or "Genres not listed"
        st.caption(
            f"{genres}  |  {show.get('language') or 'Language unknown'}  |  "
            f"{show.get('status') or 'Status unknown'}"
        )
        metrics = st.columns(4)
        metrics[0].metric("TVMaze rating", f"{show_rating(show)} / 10")
        metrics[1].metric("Episodes", len(episodes))
        metrics[2].metric("Runtime", f"{show.get('averageRuntime') or show.get('runtime') or '—'} min")
        network = show.get("network") or show.get("webChannel") or {}
        metrics[3].metric("Network / platform", network.get("name") or "—")
        summary = plain_text(show.get("summary"))
        if summary:
            st.write(summary)
        if show.get("url"):
            st.link_button("Open on TVMaze", show["url"])

    st.markdown("### Episode guide")
    if not episodes:
        st.info("TVMaze has no episode information for this show yet.")
    else:
        seasons = sorted({episode.get("season", 0) for episode in episodes})
        season_labels = {
            season: "Specials" if season == 0 else f"Season {season}"
            for season in seasons
        }
        selected_season = st.selectbox(
            "Choose a season",
            seasons,
            format_func=lambda season: season_labels[season],
            key=f"season-{show_id}",
        )
        season_episodes = [
            episode for episode in episodes
            if episode.get("season", 0) == selected_season
        ]
        st.caption(f"{len(season_episodes)} episodes in {season_labels[selected_season].lower()}")
        rows = [
            {
                "Episode": episode.get("number") or "Special",
                "Title": episode.get("name") or "Untitled",
                "Air date": episode.get("airdate") or "Unknown",
                "Runtime": f"{episode['runtime']} min" if episode.get("runtime") else "—",
                "Rating": show_rating(episode),
            }
            for episode in season_episodes
        ]
        st.dataframe(rows, hide_index=True, use_container_width=True)
        episode_names = [
            f"{episode.get('number') or 'Special'} · {episode.get('name') or 'Untitled'}"
            for episode in season_episodes
        ]
        selected_episode_index = st.selectbox(
            "Explore an episode",
            range(len(season_episodes)),
            format_func=lambda index: episode_names[index],
            key=f"episode-{show_id}-{selected_season}",
        )
        episode = season_episodes[selected_episode_index]
        with st.container(border=True):
            st.markdown(f"#### {episode.get('name') or 'Untitled'}")
            episode_summary = plain_text(episode.get("summary"))
            if episode_summary:
                st.write(episode_summary)
            else:
                st.caption("No episode summary is available.")

    st.markdown("### Main cast")
    if not cast:
        st.caption("No cast information is listed.")
    else:
        cast_columns = st.columns(4)
        for index, member in enumerate(cast[:12]):
            person = member.get("person") or {}
            character = member.get("character") or {}
            with cast_columns[index % 4]:
                portrait = (person.get("image") or {}).get("medium")
                if portrait:
                    st.image(portrait, use_container_width=True)
                st.markdown(f"**{person.get('name', 'Unknown performer')}**")
                st.caption(f"as {character.get('name', 'Unknown character')}")


def render_series_fallback(shows: list[dict[str, Any]]) -> None:
    if not shows:
        st.info("Featured titles will appear when the catalog is available.")
        return
    columns = st.columns(min(len(shows), 5))
    for index, show in enumerate(shows[:5]):
        with columns[index]:
            with st.container(border=True):
                image = (show.get("image") or {}).get("medium")
                if image:
                    st.image(image, use_container_width=True)
                st.markdown(f"**{show.get('name', 'Untitled')}**")
                genres = " · ".join(show.get("genres") or [])
                st.caption(
                    f"{show_rating(show)} / 10"
                    + (f" · {genres}" if genres else "")
                )
                if st.button(
                    "Explore series",
                    key=f"fallback-series-{show['id']}",
                    use_container_width=True,
                ):
                    st.session_state["selected_movie_id"] = None
                    st.session_state["selected_show_id"] = show["id"]
                    st.session_state["from_home"] = True
                    st.session_state["show_results"] = [{"show": show}]
                    st.session_state["show_results_query"] = show.get("name", "")
                    st.rerun()


def render_discover_home() -> None:
    st.markdown('<div class="screen-kicker">ScreenScope · Curated for you</div>', unsafe_allow_html=True)
    st.markdown("# Stories worth staying in for.")
    st.markdown(
        '<p class="screen-subtitle">A front-row seat to the shows everyone’s talking about '
        'and the films you’ll want to queue next.</p>',
        unsafe_allow_html=True,
    )

    client = tmdb_client()
    if client is None:
        st.warning(
            "Add your TMDB read access token to see trending film and series banners. "
            "Setup: add `TMDB_READ_ACCESS_TOKEN` to `.streamlit/secrets.toml` "
            "or your deployment’s secrets."
        )
        try:
            with st.spinner("Finding top-rated series on TVMaze…"):
                shows = get_featured_series()
        except (requests.RequestException, ValueError) as error:
            st.error(f"Could not load featured series from TVMaze: {error}")
            return
        if shows:
            render_tvmaze_hero(shows[0])
        section_heading("Series spotlight", "Featured titles · TVMaze ratings")
        render_series_fallback(shows)
        section_heading("Film spotlight", "Powered by TMDB")
        st.info("Configure the TMDB token to load current film posters and trending picks.")
        return

    try:
        with st.spinner("Gathering this week’s trending picks…"):
            trending_tv = get_trending("tv")
            trending_movies = get_trending("movie")
    except (requests.RequestException, ValueError) as error:
        st.error(f"Could not load trending picks from TMDB: {error}")
        return

    if trending_tv:
        hero_tv = trending_tv[0]
        render_hero(hero_tv, "tv", "Trending series this week")
        if st.button(
            "Explore this series",
            key=f"hero-tv-{hero_tv['id']}",
            type="primary",
        ):
            open_tmdb_series(hero_tv.get("name") or "")
    section_heading("Trending series", "TVMaze powers the episode and cast details")
    render_media_row(trending_tv[1:] if trending_tv else [], "tv")

    if trending_movies:
        section_heading("Film of the week", "Trending now on TMDB")
        hero_movie = trending_movies[0]
        render_hero(hero_movie, "movie", "Film of the week")
        if st.button(
            "Explore film",
            key=f"hero-movie-{hero_movie['id']}",
            type="primary",
        ):
            st.session_state["selected_show_id"] = None
            st.session_state["selected_movie_id"] = hero_movie["id"]
            st.session_state["discover_media_type"] = "Home"
            st.rerun()
    section_heading("Trending films", "The most talked-about movies this week")
    render_media_row(trending_movies[1:] if trending_movies else [], "movie")


def page_discover() -> None:
    selected_show_id = st.session_state.get("selected_show_id")
    selected_movie_id = st.session_state.get("selected_movie_id")
    if selected_show_id:
        show_detail(selected_show_id)
        return
    if selected_movie_id:
        show_movie_detail(selected_movie_id)
        return

    media_type = st.session_state.get("discover_media_type")
    has_movie_results = media_type == "Films" and "movie_results" in st.session_state
    has_show_results = media_type == "Series" and "show_results" in st.session_state
    if has_movie_results:
        query = st.session_state.get("movie_results_query") or "your search"
        section_heading(f"Film results for “{query}”")
        render_media_row(st.session_state["movie_results"], "movie")
    elif has_show_results:
        query = st.session_state.get("show_results_query") or "your search"
        st.markdown('<div class="screen-kicker">Search results</div>', unsafe_allow_html=True)
        section_heading(f"Series results for “{query}”")
        show_search_results(st.session_state["show_results"])
    else:
        render_discover_home()

    st.divider()
    st.markdown('<div class="screen-kicker">Search the catalog</div>', unsafe_allow_html=True)
    with st.form("catalog-search"):
        controls = st.columns([4, 1.3])
        with controls[0]:
            query = st.text_input(
                "Search the catalog",
                placeholder="Search a series or film title",
            ).strip()
        with controls[1]:
            media_type = st.selectbox("I'm looking for", ["Series", "Films"])
        submitted = st.form_submit_button("Search titles", type="primary")
    if submitted:
        st.session_state.pop("discover_error", None)
        st.session_state["selected_show_id"] = None
        st.session_state["selected_movie_id"] = None
        st.session_state["from_home"] = False
        st.session_state["discover_media_type"] = media_type
        if not query:
            st.warning("Enter a title to search.")
            return
        if media_type == "Series":
            st.session_state["show_results_query"] = query
            try:
                with st.spinner(f"Searching TVMaze for “{query}”…"):
                    st.session_state["show_results"] = search_shows(query)
            except (requests.RequestException, ValueError) as error:
                st.session_state["show_results"] = []
                st.session_state["discover_error"] = f"TVMaze show search failed: {error}"
        else:
            st.session_state["movie_results_query"] = query
            if tmdb_client() is None:
                st.error("Configure a TMDB read access token before searching films.")
                st.session_state["movie_results"] = []
                return
            else:
                try:
                    with st.spinner(f"Searching TMDB for “{query}”…"):
                        st.session_state["movie_results"] = search_movies(query)
                except (requests.RequestException, ValueError) as error:
                    st.session_state["movie_results"] = []
                    st.session_state["discover_error"] = f"TMDB movie search failed: {error}"
        st.rerun()
    error = st.session_state.pop("discover_error", None)
    if error:
        st.error(error)


def page_schedule() -> None:
    st.markdown("# What’s airing?")
    st.markdown("Browse TVMaze’s local TV schedule or its streaming schedule.")
    controls = st.columns([1, 1, 2])
    with controls[0]:
        selected_date = st.date_input("Air date", value=date.today())
    with controls[1]:
        country = st.selectbox(
            "Country",
            ["US", "GB", "DE", "CA", "AU", "FR", "JP"],
            format_func=lambda code: {
                "US": "🇺🇸 United States",
                "GB": "🇬🇧 United Kingdom",
                "DE": "🇩🇪 Germany",
                "CA": "🇨🇦 Canada",
                "AU": "🇦🇺 Australia",
                "FR": "🇫🇷 France",
                "JP": "🇯🇵 Japan",
            }[code],
        )
    with controls[2]:
        streaming = st.toggle("Streaming / web schedule")
        if streaming:
            st.caption("Select “All countries” to include global streaming channels.")
    if streaming and st.checkbox("All countries", value=False):
        country = ""

    date_text = selected_date.isoformat()
    try:
        with st.spinner("Fetching the schedule…"):
            episodes = get_schedule(date_text, country, streaming)
    except (requests.RequestException, ValueError) as error:
        st.error(f"Could not load the schedule: {error}")
        return

    st.markdown(f"### {len(episodes)} episodes on {selected_date:%A, %B %-d}")
    if not episodes:
        st.info("No episodes are listed for this date and selection.")
        return

    for episode in episodes:
        show = episode.get("show") or {}
        channel = show.get("webChannel") or show.get("network") or {}
        with st.container(border=True):
            columns = st.columns([1, 4])
            with columns[0]:
                image = (show.get("image") or {}).get("medium")
                if image:
                    st.image(image, use_container_width=True)
            with columns[1]:
                title = show.get("name") or "Unknown show"
                episode_name = episode.get("name") or "Untitled episode"
                st.markdown(f"### {episode.get('airtime') or 'Time TBA'} · {title}")
                season = episode.get("season")
                number = episode.get("number")
                ep_number = f"S{season:02d}E{number:02d}" if season and number else "Special"
                st.markdown(
                    f"**{ep_number}: {episode_name}**  \n"
                    f"{channel.get('name') or 'Channel unknown'}"
                )
                summary = plain_text(episode.get("summary"))
                if summary:
                    st.write(summary)


def page_people() -> None:
    st.markdown("# People & credits")
    st.markdown("Look up an actor and explore their TVMaze cast credits.")
    with st.form("people-search"):
        query = st.text_input("Actor name", placeholder="For example, Pedro Pascal").strip()
        submitted = st.form_submit_button("Search people", type="primary")
    if submitted:
        st.session_state["person_results_query"] = query
        st.session_state["selected_person_id"] = None
        if query:
            try:
                with st.spinner(f"Searching TVMaze for “{query}”…"):
                    st.session_state["person_results"] = search_people(query)
            except (requests.RequestException, ValueError) as error:
                st.error(f"TVMaze people search failed: {error}")
                st.session_state["person_results"] = []
        else:
            st.warning("Enter a name to search.")

    results = st.session_state.get("person_results", [])
    if not results:
        st.info("Search for an actor to view their TVMaze credits.")
        return

    selected_id = st.session_state.get("selected_person_id")
    if selected_id is None:
        for item in results:
            person = item.get("person") or {}
            with st.container(border=True):
                columns = st.columns([1, 4, 1])
                image = (person.get("image") or {}).get("medium")
                with columns[0]:
                    if image:
                        st.image(image, use_container_width=True)
                with columns[1]:
                    st.markdown(f"### {person.get('name', 'Unknown performer')}")
                    country_info = person.get("country") or {}
                    details = [country_info.get("name"), person.get("gender")]
                    st.caption(" · ".join(value for value in details if value) or "No details listed")
                with columns[2]:
                    if st.button("View credits", key=f"person-{person['id']}"):
                        st.session_state["selected_person_id"] = person["id"]
                        st.rerun()
    else:
        person = next(
            (
                item["person"] for item in results
                if item.get("person", {}).get("id") == selected_id
            ),
            None,
        )
        if person is None:
            st.session_state["selected_person_id"] = None
            st.rerun()
        if st.button("← Back to people"):
            st.session_state["selected_person_id"] = None
            st.rerun()
        st.markdown(f"## {person.get('name', 'Performer')} — cast credits")
        try:
            credits = get_person_credits(selected_id)
        except (requests.RequestException, ValueError) as error:
            st.error(f"Could not load cast credits: {error}")
            return
        shows = []
        for credit in credits:
            show = (credit.get("_embedded") or {}).get("show")
            if show:
                shows.append(show)
        st.metric("TV shows credited", len(shows))
        for show in shows:
            st.markdown(
                f"- **{show.get('name', 'Untitled')}** "
                f"({show.get('premiered') or 'year unknown'}) — "
                f"{show.get('status') or 'status unknown'}"
            )


def main() -> None:
    apply_visual_theme()
    with st.sidebar:
        st.markdown("# ScreenScope")
        st.caption("Your next great watch starts here.")
        page = st.radio(
            "Browse",
            ["Discover", "Daily schedule", "People & credits"],
            label_visibility="collapsed",
        )
        st.divider()
        st.markdown("**The catalogs**")
        st.caption("TV series · TVMaze")
        st.caption("Films & weekly trends · TMDB")
        st.image(str(Path(__file__).parent / ".streamlit" / "tmdb-logo.svg"), width=150)
        st.caption(TMDB_NOTICE)
        with st.expander("About the data"):
            st.markdown(
                "[TMDB attribution](https://www.themoviedb.org/about/logos-attribution) · "
                "[TVMaze API](https://www.tvmaze.com/api)"
            )

    if page == "Discover":
        page_discover()
    elif page == "Daily schedule":
        page_schedule()
    else:
        page_people()


if __name__ == "__main__":
    main()
