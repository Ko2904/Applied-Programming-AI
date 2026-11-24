"""Streamlit storefront for the Supabase-backed Books to Scrape catalogue."""

from __future__ import annotations

import os
from html import escape
from math import ceil
from textwrap import dedent
from typing import Any
from urllib.parse import urlparse

import streamlit as st
from dotenv import load_dotenv
from supabase import create_client

from scraper import BookScraper, save_to_supabase

load_dotenv()
st.set_page_config(page_title="The Book Nook", page_icon="📚", layout="wide")
st.markdown(
    """
    <style>
    .stApp {
        background: #f7f5f0;
        color: #242a27;
    }
    section.main > div.block-container {
        max-width: 1440px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    .store-hero {
        background: linear-gradient(115deg, #173b34 0%, #285c4d 70%, #477361 100%);
        border-radius: 22px;
        color: #fff;
        margin: 0 0 2rem;
        padding: 2.2rem 2.6rem;
    }
    .store-hero .eyebrow {
        color: #e7c982;
        font-size: .75rem;
        font-weight: 700;
        letter-spacing: .16em;
        margin: 0 0 .65rem;
        text-transform: uppercase;
    }
    .store-hero h1 {
        color: #fff;
        font-family: Georgia, "Times New Roman", serif;
        font-size: clamp(2rem, 5vw, 3.4rem);
        line-height: 1.1;
        margin: 0 0 .7rem;
    }
    .store-hero h1 em {
        color: #e7c982;
        font-weight: 400;
    }
    .store-hero .hero-copy {
        color: #e4ece7;
        font-size: 1rem;
        margin: 0;
        max-width: 620px;
    }
    .book-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1.25rem;
        margin: 1rem 0 2.5rem;
    }
    .book-card {
        background: #fff;
        border: 1px solid #e8e4dc;
        border-radius: 16px;
        box-shadow: 0 5px 18px rgba(32, 45, 37, .055);
        display: flex;
        flex-direction: column;
        min-width: 0;
        overflow: hidden;
        transition: box-shadow .18s ease, transform .18s ease;
    }
    .book-card:hover {
        box-shadow: 0 12px 28px rgba(32, 45, 37, .12);
        transform: translateY(-3px);
    }
    .book-cover {
        align-items: center;
        background: #f0eee8;
        display: flex;
        height: 260px;
        justify-content: center;
        padding: 1.25rem;
    }
    .book-cover img {
        height: 100%;
        max-width: 100%;
        object-fit: contain;
        transition: transform .2s ease;
    }
    .book-card:hover .book-cover img {
        transform: scale(1.035);
    }
    .cover-placeholder {
        color: #8e958e;
        font-family: Georgia, "Times New Roman", serif;
        font-size: 1.1rem;
        text-align: center;
    }
    .book-info {
        display: flex;
        flex: 1;
        flex-direction: column;
        padding: 1rem 1.1rem 1.15rem;
    }
    .book-title {
        color: #263b32;
        display: -webkit-box;
        font-family: Georgia, "Times New Roman", serif;
        font-size: 1.05rem;
        font-weight: 700;
        line-height: 1.35;
        margin: 0 0 .6rem;
        min-height: 2.8em;
        overflow: hidden;
        -webkit-box-orient: vertical;
        -webkit-line-clamp: 2;
    }
    .book-rating {
        align-items: center;
        color: #737b75;
        display: flex;
        font-size: .82rem;
        gap: .4rem;
        margin-bottom: .85rem;
    }
    .book-stars {
        color: #d3a640;
        letter-spacing: .08em;
    }
    .book-footer {
        align-items: center;
        border-top: 1px solid #f0eee8;
        display: flex;
        gap: .5rem;
        justify-content: space-between;
        margin-top: auto;
        padding-top: .8rem;
    }
    .book-price {
        color: #245342;
        font-size: 1.08rem;
        font-weight: 750;
        white-space: nowrap;
    }
    .book-availability {
        border-radius: 999px;
        font-size: .7rem;
        font-weight: 650;
        padding: .3rem .55rem;
        text-align: center;
    }
    .book-availability.in-stock {
        background: #e8f3eb;
        color: #286440;
    }
    .book-availability.out-of-stock {
        background: #f7e9e5;
        color: #994d3d;
    }
    @media (max-width: 1050px) {
        .book-grid { grid-template-columns: repeat(3, minmax(0, 1fr)); }
    }
    @media (max-width: 760px) {
        .book-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: .8rem; }
        .book-cover { height: 220px; }
        .book-info { padding: .85rem; }
        .store-hero { padding: 1.6rem; }
    }
    @media (max-width: 430px) {
        .book-grid { grid-template-columns: 1fr; }
        .book-cover { height: 280px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="store-hero">
      <p class="eyebrow">The Book Nook · Curated from Books to Scrape</p>
      <h1>Your next favorite<br><em>is waiting.</em></h1>
      <p class="hero-copy">Browse the collection, find a new read, and keep an eye on prices over time.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
if not url or not key:
    st.error("Configure SUPABASE_URL and SUPABASE_KEY in your local .env file.")
    st.stop()

client = create_client(url, key)
with st.sidebar:
    st.header("Catalogue tools")
    st.caption("Refresh the collection from the demo bookstore.")
    pages = st.number_input("Maximum pages to scrape", min_value=1, max_value=50, value=1)
    if st.button("Scrape and save", type="primary", use_container_width=True):
        with st.spinner("Fetching books and updating Supabase..."):
            scraper = BookScraper()
            scraped_books = scraper.scrape(max_pages=int(pages))
            save_to_supabase(scraped_books, scraper.pages_scraped)
        st.success(f"Saved {len(scraped_books)} books from {scraper.pages_scraped} page(s).")
        st.rerun()

books_result = (
    client.table("books")
    .select("id, title, price, currency, availability, rating, source_url, image_url, last_seen_at")
    .order("title")
    .limit(1000)
    .execute()
)
books: list[dict[str, Any]] = books_result.data

st.subheader("Shop the collection")
search_col, sort_col = st.columns([2, 1])
with search_col:
    search = st.text_input("Search books", placeholder="Search by title...", label_visibility="collapsed")
with sort_col:
    sort_order = st.selectbox(
        "Sort books",
        ["Title A–Z", "Price: low to high", "Price: high to low", "Top rated"],
        label_visibility="collapsed",
    )

filtered_books = [
    book for book in books if search.strip().casefold() in book["title"].casefold()
]
if sort_order == "Price: low to high":
    filtered_books.sort(key=lambda book: (float(book["price"]), book["title"].casefold()))
elif sort_order == "Price: high to low":
    filtered_books.sort(key=lambda book: (-float(book["price"]), book["title"].casefold()))
elif sort_order == "Top rated":
    filtered_books.sort(
        key=lambda book: (-(int(book["rating"]) if book["rating"] is not None else 0), book["title"].casefold())
    )

if not books:
    st.info("Your shelves are empty. Use **Scrape and save** in the sidebar to add books.")
elif not filtered_books:
    st.info("No books match that search. Try another title.")
else:
    st.caption(f"{len(filtered_books)} {('book' if len(filtered_books) == 1 else 'books')} in the collection")
    page_size = 24
    page_count = ceil(len(filtered_books) / page_size)
    if st.session_state.get("catalogue_filter") != (search, sort_order):
        st.session_state.catalogue_page = 1
        st.session_state.catalogue_filter = (search, sort_order)
    current_page = min(st.session_state.get("catalogue_page", 1), page_count)
    st.session_state.catalogue_page = current_page

    start = (current_page - 1) * page_size
    page_books = filtered_books[start : start + page_size]
    cards: list[str] = []
    for book in page_books:
        title = escape(str(book["title"]))
        image_url = str(book.get("image_url") or "")
        source_url = str(book.get("source_url") or "")
        safe_image = (
            escape(image_url, quote=True)
            if urlparse(image_url).scheme == "https"
            and urlparse(image_url).hostname == "books.toscrape.com"
            else ""
        )
        safe_source = (
            escape(source_url, quote=True)
            if urlparse(source_url).scheme == "https"
            and urlparse(source_url).hostname == "books.toscrape.com"
            else ""
        )

        cover = (
            f'<img src="{safe_image}" alt="Cover of {title}" loading="lazy">'
            if safe_image
            else '<span class="cover-placeholder">Cover unavailable</span>'
        )
        cover_link = (
            f'<a class="book-cover" href="{safe_source}" target="_blank" rel="noopener noreferrer">{cover}</a>'
            if safe_source
            else f'<div class="book-cover">{cover}</div>'
        )
        rating = book.get("rating")
        rating_html = ""
        if rating is not None:
            rating_value = int(rating)
            rating_html = (
                f'<div class="book-rating" aria-label="Rating {rating_value} out of 5">'
                f'<span class="book-stars">{"★" * rating_value}{"☆" * (5 - rating_value)}</span>'
                f"<span>{rating_value}/5</span></div>"
            )

        currency = str(book.get("currency") or "GBP")
        currency_symbol = {"GBP": "£", "USD": "$", "EUR": "€"}.get(currency, f"{currency} ")
        price = f"{currency_symbol}{float(book['price']):.2f}"
        availability = str(book.get("availability") or "Availability unknown")
        in_stock = "in stock" in availability.casefold()
        stock_label = "In stock" if in_stock else "Unavailable"
        stock_class = "in-stock" if in_stock else "out-of-stock"

        cards.append(
            dedent(
                f"""
                <article class="book-card">
                  {cover_link}
                  <div class="book-info">
                    <h3 class="book-title" title="{title}">{title}</h3>
                    {rating_html}
                    <div class="book-footer">
                      <span class="book-price">{escape(price)}</span>
                      <span class="book-availability {stock_class}">{stock_label}</span>
                    </div>
                  </div>
                </article>
                """
            ).strip()
        )
    st.markdown(
        f'<div class="book-grid">{"".join(cards)}</div>',
        unsafe_allow_html=True,
    )

    previous_col, page_col, next_col = st.columns([1, 2, 1])
    with previous_col:
        if st.button("← Previous", disabled=current_page == 1, use_container_width=True):
            st.session_state.catalogue_page = current_page - 1
            st.rerun()
    with page_col:
        st.markdown(
            f'<p style="text-align:center; padding-top:.35rem">Page {current_page} of {page_count}</p>',
            unsafe_allow_html=True,
        )
    with next_col:
        if st.button("Next →", disabled=current_page == page_count, use_container_width=True):
            st.session_state.catalogue_page = current_page + 1
            st.rerun()

    with st.expander("View price history"):
        selected = st.selectbox("Choose a book", books, format_func=lambda book: book["title"])
        history = (
            client.table("price_history")
            .select("price, observed_at")
            .eq("book_id", selected["id"])
            .order("observed_at")
            .execute()
            .data
        )
        if history:
            st.line_chart(
                [
                    {"Observed at": point["observed_at"], "Price": float(point["price"])}
                    for point in history
                ],
                x="Observed at",
                y="Price",
            )
        else:
            st.info("No price changes have been recorded for this book yet.")
