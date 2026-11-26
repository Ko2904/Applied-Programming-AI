# Books to Scrape — catalogue scraper and storefront

## Purpose

This project collects book listings from the Books to Scrape practice website.
It can save a local JSON snapshot, store catalogue records and price changes
in Supabase, and show saved data in an interactive Streamlit storefront.

## Data collection

The scraper requests catalogue listing pages from
[books.toscrape.com](https://books.toscrape.com/). It records a book's title,
price, currency, availability, rating, source URL, and image URL. It follows
the catalogue's pagination and does not request individual detail pages. This
is a practice site with sample catalogue data, not a live retail source.

## Data persistence

The CLI can write a JSON snapshot to a local file such as `books.json`.
Optionally, Supabase stores the current book records, scrape-run metadata, and
price history. Repeated scrapes update each book, and a price-history record is
added when its price differs from the last recorded price. The Streamlit
storefront reads these Supabase tables. Local JSON supports simple exports;
Supabase enables the app to share and query saved catalogue and history data.

## User interaction

Run the scraper from a terminal with `--limit` to cap the number of books,
`--pages` to cap the pages visited, and `--output books.json` to save a JSON
snapshot. Add `--save-to-supabase` to persist a scrape in the configured
database. In the Streamlit app, use the sidebar to scrape and save, search and
sort the catalogue, navigate its pages, and view a selected book's price
history.

## Setup

The project was tested with Python 3.11.

From this directory, create and activate a virtual environment and install
dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

For a local JSON scrape, no database configuration is needed:

```bash
python scraper.py --limit 5 --output books.json
```

To use Supabase, create a project and run [`schema.sql`](./schema.sql) in its
SQL Editor. Create a `.env` file in this directory:

```dotenv
SUPABASE_URL=https://YOUR_PROJECT_ID.supabase.co
SUPABASE_KEY=YOUR_SERVICE_ROLE_KEY
```

Replace the placeholders with your project URL and server-side service-role
key. Keep the key secret: do not use it in a browser, commit `.env`, or share
the value. The `.gitignore` excludes `.env` and `books.json`. Start the
Streamlit app with Supabase configured:

```bash
streamlit run app.py
```

Run the tests from this directory with `python -m unittest discover -s tests
-v`. The Python dependencies are listed in [`requirements.txt`](./requirements.txt).

## Learning

The project practices HTML parsing, pagination, request timeouts, command-line
options, database upserts, and interactive data presentation. A key design
challenge is retaining price history without adding duplicate observations:
each scrape compares a book's price with its most recent saved price before
inserting a history row. The schema and scraper also distinguish current book
state from scrape-run metadata and historical changes.

## Limitations and assistance

The scraper only reads listing pages and depends on the practice site's
availability and HTML structure. The sample catalogue is not current retail
data. Supabase features require an internet connection, configured tables, and
a service-role key. Scrapes should remain small and respectful.

The project uses the third-party Python packages listed in
[`requirements.txt`](./requirements.txt), plus the Supabase service and the
Books to Scrape website. No externally copied source-code snippets are
identified in this project; dependencies and services are used through their
documented interfaces. The repository's MIT license covers original project
code only; see [the third-party notices](../THIRD_PARTY_NOTICES.md) for
content exclusions.
