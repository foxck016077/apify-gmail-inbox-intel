# Changelog

All notable changes to this project. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows [SemVer](https://semver.org/).

## [Unreleased]

### Planned
- Cover-image for the Apify Store listing
- `thread_search` pagination edge: empty `nextPageToken` after partial result
- Optional per-tenant `kvs` namespace prefix for multi-account dev setups

## [0.1.0] — 2026-05-16

First public release.

### Added
- Four core features behind a single Actor entrypoint
  - `thread_search` — Gmail thread search with metadata + message counts
  - `reply_metrics` — per-thread reply tracking, last reply age, SLA breach flag
  - `summarizer` — optional OpenAI thread summary (bring-your-own API key)
  - `unread_digest` — last N hours of unread threads, grouped by label
- Refresh-token-only OAuth flow — access token lives only in memory for the run
- Per-feature monthly quota via Apify `KeyValueStore` (no external DB, no cron)
- Async router with feature-scoped error semantics
- `dry_run` mode that skips real Gmail API calls for safe testing
- 6 pytest tests (`asyncio_mode=auto`) covering the happy path of each feature
- CI workflow on Python 3.10 / 3.11 / 3.12
- `examples/` directory with 5 ready-to-paste input JSON files
- `SECURITY.md` (private advisory, 72-hour ack SLA) + dependabot weekly updates
- 5-part design notes series on dev.to ([series index](https://dev.to/foxck016077/series/39719))
- MIT license

### Known limitations
- Apify Store listing not published yet (under review)
- No cover image yet — only icon + 2 static screenshots
- LLM summary cost is passed through to the user (no markup, no built-in caching)

[Unreleased]: https://github.com/foxck016077/apify-gmail-inbox-intel/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/foxck016077/apify-gmail-inbox-intel/releases/tag/v0.1.0
