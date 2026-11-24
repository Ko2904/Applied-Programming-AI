"""Scrape catalogue listings from the Books to Scrape practice website."""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://books.toscrape.com/"
USER_AGENT = "APAI-Scraper/1.0 (educational catalogue scraper)"
RATING_VALUES = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


@dataclass(frozen=True)
class Book:
    source_url: str
    title: str
    price: float
    currency: str
    availability: str
    rating: int | None
    image_url: str


def parse_listing(html: str, page_url: str) -> list[Book]:
    """Parse books from one catalogue page."""
    soup = BeautifulSoup(html, "html.parser")
    books: list[Book] = []
    for article in soup.select("article.product_pod"):
        link = article.select_one("h3 a")
        price_tag = article.select_one(".price_color")
        availability_tag = article.select_one(".availability")
        image = article.select_one("img")
        rating_tag = article.select_one(".star-rating")
        if not (link and price_tag and availability_tag and image and rating_tag):
            raise ValueError(f"Incomplete book listing on {page_url}")

        title = link.get("title") or link.get_text(strip=True)
        price_text = price_tag.get_text(strip=True).replace("£", "").strip()
        try:
            price = float(price_text)
        except ValueError as exc:
            raise ValueError(f"Invalid price {price_text!r} on {page_url}") from exc

        rating_class = next(
            (name for name in rating_tag.get("class", []) if name != "star-rating"),
            None,
        )
        books.append(
            Book(
                source_url=urljoin(page_url, str(link.get("href"))),
                title=title,
                price=price,
                currency="GBP",
                availability=availability_tag.get_text(" ", strip=True),
                rating=RATING_VALUES.get(rating_class or ""),
                image_url=urljoin(page_url, str(image.get("src"))),
            )
        )
    return books


class BookScraper:
    def __init__(self, delay: float = 0.25, timeout: float = 20) -> None:
        self.delay = delay
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.pages_scraped = 0

    def scrape(self, limit: int | None = None, max_pages: int | None = None) -> list[Book]:
        if limit is not None and limit < 1:
            raise ValueError("limit must be at least 1")
        if max_pages is not None and max_pages < 1:
            raise ValueError("pages must be at least 1")

        books: list[Book] = []
        page_url = BASE_URL
        while page_url and (max_pages is None or self.pages_scraped < max_pages):
            response = self.session.get(page_url, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding
            page_books = parse_listing(response.text, response.url)
            self.pages_scraped += 1
            books.extend(page_books)
            if limit is not None and len(books) >= limit:
                return books[:limit]

            next_link = BeautifulSoup(response.text, "html.parser").select_one("li.next a")
            page_url = (
                urljoin(response.url, str(next_link.get("href")))
                if next_link and (max_pages is None or self.pages_scraped < max_pages)
                else ""
            )
            if page_url and self.delay:
                time.sleep(self.delay)
        return books


def save_to_supabase(books: list[Book], pages_scraped: int) -> None:
    """Upsert current book data and append rows for newly observed prices."""
    from dotenv import load_dotenv

    load_dotenv()
    import os

    from supabase import create_client

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        raise RuntimeError("Set SUPABASE_URL and SUPABASE_KEY before saving to Supabase.")

    client = create_client(supabase_url, supabase_key)
    run_result = (
        client.table("scrape_runs")
        .insert({"status": "running", "pages_scraped": pages_scraped, "books_scraped": len(books)})
        .execute()
    )
    run_id = run_result.data[0]["id"]
    try:
        for book in books:
            record: dict[str, Any] = asdict(book)
            record["last_seen_at"] = datetime.now(timezone.utc).isoformat()
            saved = (
                client.table("books")
                .upsert(record, on_conflict="source_url")
                .execute()
                .data[0]
            )
            previous = (
                client.table("price_history")
                .select("price")
                .eq("book_id", saved["id"])
                .order("observed_at", desc=True)
                .limit(1)
                .execute()
                .data
            )
            if not previous or float(previous[0]["price"]) != book.price:
                client.table("price_history").insert(
                    {"book_id": saved["id"], "scrape_run_id": run_id, "price": book.price}
                ).execute()

        client.table("scrape_runs").update(
            {"status": "completed", "completed_at": datetime.now(timezone.utc).isoformat()}
        ).eq("id", run_id).execute()
    except Exception as exc:
        client.table("scrape_runs").update(
            {
                "status": "failed",
                "completed_at": datetime.now(timezone.utc).isoformat(),
                "error": str(exc)[:1000],
            }
        ).eq("id", run_id).execute()
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="maximum number of books to scrape")
    parser.add_argument("--pages", type=int, help="maximum number of catalogue pages to visit")
    parser.add_argument("--output", type=Path, help="write scraped books as JSON to this file")
    parser.add_argument("--save-to-supabase", action="store_true", help="save books to Supabase")
    args = parser.parse_args(argv)

    try:
        scraper = BookScraper()
        books = scraper.scrape(limit=args.limit, max_pages=args.pages)
        if args.output:
            args.output.write_text(
                json.dumps([asdict(book) for book in books], indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
        if args.save_to_supabase:
            save_to_supabase(books, scraper.pages_scraped)
        if not args.output and not args.save_to_supabase:
            print(json.dumps([asdict(book) for book in books], indent=2, ensure_ascii=False))
        print(f"Scraped {len(books)} books from {scraper.pages_scraped} page(s).", file=sys.stderr)
        return 0
    except (requests.RequestException, ValueError, RuntimeError) as exc:
        print(f"Scrape failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
