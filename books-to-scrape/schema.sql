create extension if not exists pgcrypto;

create table if not exists public.books (
    id uuid primary key default gen_random_uuid(),
    source_url text not null unique,
    title text not null,
    price numeric(10, 2) not null check (price >= 0),
    currency text not null default 'GBP',
    availability text not null,
    rating smallint check (rating between 1 and 5),
    image_url text not null,
    last_seen_at timestamptz not null default now()
);

create table if not exists public.scrape_runs (
    id uuid primary key default gen_random_uuid(),
    started_at timestamptz not null default now(),
    completed_at timestamptz,
    status text not null check (status in ('running', 'completed', 'failed')),
    pages_scraped integer not null default 0,
    books_scraped integer not null default 0,
    error text
);

create table if not exists public.price_history (
    id bigint generated always as identity primary key,
    book_id uuid not null references public.books(id) on delete cascade,
    scrape_run_id uuid not null references public.scrape_runs(id) on delete cascade,
    price numeric(10, 2) not null check (price >= 0),
    observed_at timestamptz not null default now(),
    unique (book_id, scrape_run_id)
);

create index if not exists price_history_book_observed_idx
    on public.price_history (book_id, observed_at desc);

grant select, insert, update, delete
    on table public.books, public.scrape_runs, public.price_history
    to service_role;
