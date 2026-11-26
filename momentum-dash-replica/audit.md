# Public-repository audit

**Scope:** Repository-wide static publication audit, included here with the
New Tab Dashboard project. Findings apply across all three project folders
unless noted. The audit follows the submission checklist and did not execute
project code, print secret values, commit, or push. Requested README and audit
documents are separate task changes.

## 1. Issues to resolve before publishing

### Confirmed — tracked macOS metadata

These macOS `.DS_Store` files are tracked:

- `books-to-scrape/.DS_Store`
- `momentum-dash-replica/.DS_Store`
- `momentum-dash-replica/scripts/.DS_Store`

They are machine-generated metadata and may contain local folder information.
Their presence also confirms that the current ignore rules do not exclude them.

**Steps:** Add `.DS_Store` to a repository-root `.gitignore`, then remove the
three files from Git tracking (for example, `git rm --cached` with those exact
paths). Review the resulting diff before publishing.

### Possible concern — extension news source points to a different repository

`momentum-dash-replica/newtab.js` fetches news from the raw
`Ko2904/Applied-Programming-Chrome-Extension` repository, while this project
also contains `momentum-dash-replica/news.json`. It is not clear whether the
external repository is the intended canonical source.

**Steps:** Confirm that the URL is intentional and that the target repository
is public and maintained. If this repository should supply the extension's
news, point the extension to its own bundled `news.json` or update the URL and
host permission to the intended public repository.

## 2. Recommended improvements

- **Repository-wide ignore rules:** There is no root `.gitignore`; current
  rules are project-local. Add root-level rules for common OS metadata,
  Python virtual environments/caches, and Node dependency/build output so
  files created at the repository root are excluded too.
- **Third-party content and licensing:** The repository has no `LICENSE`.
  Before redistribution, choose a license for your own code and review
  obligations for TVMaze CC BY-SA data, TMDB attribution and images, the
  bookstore practice-site content, bundled quotes, and the news headline and
  summary excerpts. The extension's news generator is in
  `momentum-dash-replica/scripts/generate-news.js`; its output is committed in
  `momentum-dash-replica/news.json`.
- **Automated coverage:** The Python folders have unit tests; the Chrome
  extension has no automated tests. Consider adding a small test for the
  extension's data rendering and failure fallback.
- **Secret history:** The tracked-text review did not identify obvious
  hard-coded credentials. This does not inspect every possible encoding or
  historical Git object.

## 3. Resolution steps

1. Add a root `.gitignore` that covers `.DS_Store`, `.venv/`, `venv/`,
   `__pycache__/`, `*.py[cod]`, `node_modules/`, and generated build/cache
   directories. Keep any intentional generated files, such as the extension's
   published `news.json`, explicitly tracked.
2. Stop tracking the three `.DS_Store` paths listed above and verify they no
   longer appear in `git ls-files`.
3. Confirm or update the extension's `NEWS_URL` in `momentum-dash-replica/newtab.js`.
4. Select and add a repository license only after confirming that project
   assets and third-party data may be redistributed under the chosen terms.
5. Run the project tests and manually verify API- or credential-dependent
   features in an appropriately configured local environment.

## 4. Could not verify

- No API service-role key, TMDB token, or Event Registry key was available for
  validation; the audit did not inspect any untracked local secrets.
- No application code, tests, network requests, or GitHub Actions workflow was
  executed as part of this static audit.
- Historical Git objects were not scanned for credentials.
- The licensing/redistribution terms for all bundled third-party content and
  the intended canonical extension news URL require owner confirmation.
- The initial Git status was clean before the requested documentation changes;
  the audit itself did not commit or push.

No obvious credential was found in the focused tracked-text scan. That is not
proof that the repository or its history is safe to publish.

## Follow-up status (2026-11-26)

- Added a repository-root `.gitignore`; the three listed `.DS_Store` files are
  no longer tracked and are ignored locally.
- Updated the root README to describe the bundled news feed, and added ignore
  rules for dotenv files and Streamlit secrets.
- The extension's news feature, generated feed, and workflow were removed;
  its README now documents locally stored reminder, to-do, and goal widgets.
  The broad host permission is absent.
- Books to Scrape's 2 tests, TVMaze's 7 tests, and the extension's 5 Node tests
  pass. Extension JavaScript syntax and manifest/feed JSON validation also pass.
- Added an MIT license limited to original project code and a third-party
  notices file; third-party content remains excluded and subject to rights
  review. A signature-based scan of available Git history found no matches,
  but cannot rule out other formats or unscanned remote history. API- and
  credential-dependent behavior was not manually verified.
