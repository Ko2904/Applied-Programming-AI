# APAI Scraper

A staged scraper for the [Books to Scrape](https://books.toscrape.com/) demo site. It can write JSON locally, store books and price changes in Supabase, and show the data in a small Streamlit dashboard.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

For Supabase features, create a project and run [`schema.sql`](schema.sql) in the Supabase SQL Editor. It creates the tables and grants the server-side `service_role` the permissions the scraper needs; rerun it to apply schema updates. Copy `.env.example` to `.env` and set your project URL and **server-side secret/service-role key** (not the publishable key). Do not commit `.env` or expose this key in a browser. The app loads `.env` automatically.

## Step 1: run the isolated scraper

Run a small test crawl (no Supabase account required):

```bash
python scraper.py --limit 5 --output books.json
```

Expand gradually by limiting the number of pages:

```bash
python scraper.py --pages 2 --output books.json
python scraper.py --pages 5 --output books.json
python scraper.py --output books.json
```

By default, the scraper pauses briefly between pages. `--limit` caps the total books; `--pages` caps pages. The script follows the site's pagination and records title, price, currency, availability, rating, and source/image URLs.

## Steps 3–4: save to Supabase

After setting `SUPABASE_URL` and `SUPABASE_KEY` in `.env`, try a small database run first:

```bash
python scraper.py --limit 5 --save-to-supabase
```

Then expand:

```bash
python scraper.py --pages 2 --save-to-supabase
python scraper.py --save-to-supabase
```

The schema separates the current book record, scrape-run metadata, and price changes. Repeated runs update each book and add a price-history row only when its price differs from the last recorded price.

## Step 5: dashboard

With Supabase configured, run:

```bash
.venv/bin/streamlit run app.py
```

The dashboard lists stored books, charts recorded price changes, and can launch a scrape. Leave it on a small page limit while testing, then increase it as desired.

## Notes

- Books to Scrape is a purpose-built practice site; its displayed prices/ratings are sample data.
- This project only visits the catalogue listing pages and does not fetch each book's detail page.
- If you have not created a Supabase project yet, create one at [supabase.com](https://supabase.com/), run the schema SQL, and add the URL and secret key to your local `.env`.
