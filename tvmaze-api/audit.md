# ScreenScope - Publication Audit

**Reviewed:** 2026-11-26
**Scope:** Current ScreenScope files and shared publication policies. No
secret values or local credentials were inspected.

## 1. Issues to resolve before publishing

No confirmed publication blockers were found.

- Setup, dependencies, API configuration, data handling, limitations, and
  tests are documented in the project README.
- `.streamlit/secrets.toml` is ignored and is not tracked.
- The app displays TMDB's required notice and an approved TMDB logo, and links
  to TMDB attribution guidance. The current TMDB FAQ says the free API is for
  non-commercial use; commercial use requires a separate license.
- The app links to TVMaze and documents the API's CC BY-SA 4.0 licensing and
  share-alike requirements.
- The repository license is limited to original project code. Third-party
  API data and images are excluded and described in `THIRD_PARTY_NOTICES.md`.

## 2. Recommended improvements

- Recheck provider terms and attribution requirements before any commercial
  deployment or substantial redistribution of API data or images.
- Keep the TMDB token in Streamlit secrets or an environment variable; never
  commit it.

## 3. Resolution steps

No publication-blocking changes remain for this project. The focused API
client test suite passed: 7 tests.

## 4. Could not verify

- No live TVMaze or TMDB API requests were made, and no TMDB credential was
  tested.
- A deployed Streamlit instance and its credential configuration were not
  reviewed.
- Provider terms can change; this audit is not legal advice.
- This static review cannot prove that every possible secret or sensitive
  value is absent from all historical Git objects.
