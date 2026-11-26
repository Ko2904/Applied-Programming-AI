# Applied Programming & AI — individual projects

This repository contains three small, independent projects built while learning
web APIs, data collection, persistence, browser extensions, and interactive
interfaces. Each project has its own dependencies and setup instructions.

## Projects

| Project | What it does | Main technologies |
| --- | --- | --- |
| [Books to Scrape](./books-to-scrape/) | Scrapes the Books to Scrape practice catalogue, optionally saves catalogue and price history to Supabase, and displays it in a Streamlit storefront. | Python, requests, Beautiful Soup, Streamlit, Supabase |
| [ScreenScope](./tvmaze-api/) | Searches TV series, episodes, cast, schedules, people, and film recommendations using the TVMaze and TMDB APIs. | Python, Streamlit, TVMaze API, TMDB API |
| [New Tab Dashboard](./momentum-dash-replica/) | Replaces the Chrome new-tab page with a clock, original daily note, reminders, a to-do list, a personal goal tracker, and customizable backgrounds. | Chrome Extensions, JavaScript, HTML, CSS |

## Data collection and persistence

- **Books to Scrape** requests catalogue listing pages from
  [books.toscrape.com](https://books.toscrape.com/). The command-line scraper
  can write a local JSON file or persist book records and price changes in a
  Supabase project. The Streamlit app reads from that database and can start a
  scrape. The site is a practice catalogue, not a source of real retail data.
- **ScreenScope** retrieves series, schedule, and people data from TVMaze, and
  trending series, films, and film details from TMDB. Streamlit caches API
  responses temporarily; the app does not maintain its own database. Film and
  trending features require a TMDB read access token.
- **New Tab Dashboard** uses original bundled daily notes and does not fetch
  news or contact an external data service. Reminders, to-do items, goal
  progress, selected background, and uploaded background image are stored in
  Chrome local storage in the user's browser profile.

The Python projects contact external services when their relevant features
are used. Review each README for API requirements, credentials, data handling,
and limitations before running it. The Chrome extension operates locally.

## User interaction

The Books to Scrape project is operated through scraper command-line options
and a Streamlit catalogue with search, sorting, pagination, price history, and
a scrape action. ScreenScope uses Streamlit search and navigation controls.
The Chrome extension responds to new-tab visits and lets users manage
reminders, tasks, and a personal goal, as well as select or upload a background.

## Run a project

Clone the repository, then follow the README in the project folder you want to
use:

- [Books to Scrape setup](./books-to-scrape/README.md)
- [ScreenScope setup](./tvmaze-api/README.md)
- [New Tab Dashboard setup](./momentum-dash-replica/README.md)

The two Python projects have separate `requirements.txt` files. Create and
activate a virtual environment inside the relevant project directory before
installing its requirements. The browser extension does not require an npm
package installation; Chrome loads its files directly.

## Learning goals

The projects demonstrate HTML parsing and respectful, limited scraping;
working with REST APIs and HTTP errors; storing data and tracking changes in a
database; building interactive Streamlit pages; using browser extension APIs
and local storage; and building personal productivity widgets.

## License and third-party content

Original project code is licensed under the [MIT License](./LICENSE).
Third-party data, text, images, logos, and other materials are excluded from
that license and remain subject to their own terms. See
[THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md) before redistributing
project content.

## Limitations

These are learning projects, not production services. The Python projects
depend on external websites, APIs, credentials, network availability, and
third-party terms and rate limits. The bookstore content is sample data.
ScreenScope does not guarantee that provider data is complete or current.
Extension reminders are displayed when a new tab is open; they do not send
system notifications. Widget data is local to the browser profile and is not
synchronized. Do not commit API keys, Supabase service-role credentials, local
secrets, or personal data.

## Tests

The Python projects include focused unit tests. Run them from the corresponding
project directory:

```bash
python -m unittest discover -s tests -v
```

The extension tests use Node.js's built-in test runner. Run `npm test` from
`momentum-dash-replica/`; no npm packages need to be installed.
