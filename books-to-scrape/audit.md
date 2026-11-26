# Books to Scrape - Publication Audit

**Reviewed:** 2026-11-26
**Scope:** The Books to Scrape project and shared repository publication
policies. The file and Git-state review was static. The Books to Scrape unit
tests passed: 2 tests. No secret values were read or printed.

## 1. Issues to resolve before publishing

No confirmed publication blockers were found in the current project files or
Git index. The project owner confirms that scraping the Books to Scrape
practice catalogue is intentional.

## 2. Recommended improvements

- Keep the local `.env` out of Git and rotate its credentials if they were
  ever exposed elsewhere.
- Keep dependency versions under review; a lock file can improve
  reproducibility when exact environments are required.
- Continue to scrape modestly and follow the source site's current terms.

## 3. Resolution steps

No code or configuration changes are required based on this audit. Before
publishing, verify that only intended files are staged and that `.env` remains
ignored. The README documents Python 3.11, the tested version.

## 4. Could not verify

- `books-to-scrape/.env` exists locally, is ignored, and is not tracked. Its
  contents were not inspected.
- No Supabase connection or credential was tested.
- The source site's current terms were not independently reviewed; the owner
  confirms that scraping this practice site is intended.
- Pattern-based checks found no common credential signatures or obvious
  personal-data patterns in tracked project text or available Git history.
  Such checks cannot detect every secret format or prove that the repository
  is safe.
