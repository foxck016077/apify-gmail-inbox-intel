# Changelog

All notable changes to this project. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versioning follows [SemVer](https://semver.org/).

## [Unreleased]

### Planned
- Cover-image for the Apify Store listing (Console UI upload, API field gated)
- `thread_search` pagination edge: empty `nextPageToken` after partial result
- Optional per-tenant `kvs` namespace prefix for multi-account dev setups

## 2026-05-22 — Day 13/14 build 0.1.36-0.1.38 + ZERO-TEN audit cycle

### Added
- `reply_metrics` per-thread `priority_band` field on over-SLA threads — `HOT` (ratio < 1.5×), `WARM` (1.5-3×), `COLD` (≥ 3×) of `days_since_last_reply` to `sla_days`. Summary block returns `priority_breakdown: {HOT, WARM, COLD}` counts for Friday triage at-a-glance
- `src/main.py` `dry_run` demo data extends `reply_metrics` synthetic output to include a `COLD` example so the no-OAuth demo shows all 3 bands
- `tests/test_reply_metrics.py` adds `test_priority_band` covering HOT/WARM/COLD boundaries and the `sla_days=0` edge case
- `INPUT_SCHEMA.json` `dry_run` field — `prefill: true` so the first-time Apify Console input form lands with the demo checkbox already ticked. Renamed to `"Try demo (no OAuth needed)"` and reordered to position 2 (above the OAuth block) so cold visitors see the no-OAuth path first
- GitHub Discussion #17 — Build 0.1.36 announcement + cross-link to dev.to Day 12-14 (confession layer + 13-day raw data gist)

### Changed
- README `Sample output (reply_metrics)` replaces marketing-copy `stalled_score` (never in the code) with the real shipped fields (`days_since_last_reply` / `over_sla` / `priority_band` / `reply_chain_length` / `sender_domain`)
- README quickstart leads with `"Try the demo first"` instead of `"paste 3 OAuth fields"`
- Apify Store actor `categories` PUT — was `[LEAD_GENERATION, AUTOMATION]`, now `[LEAD_GENERATION, AUTOMATION, BUSINESS]` opening a third category-page surface for solo founders / consultant cohort. `PRODUCTIVITY` is not in the Apify Store enum (verified by enum probe)
- `INPUT_SCHEMA.json` `required` trimmed to `["feature"]` only — OAuth block no longer blocks the demo path

### Fixed
- 10 dev.to articles missing `cover_image` backfilled to the canonical GitHub raw cover URL. Verified by anonymous fetch of each article's `<meta property="og:image">`. Earlier `7/7 verified` claim was a confirmation-bias false positive — logged at `buglog.jsonl#bug-20260522-0013`
- Independent audit of `~/agents/freelancer/count_replies.py` — the `7-day client reply thread = 9` metric is 9/9 `noreply@notifications.freelancer.com` digest mail across 542 cumulative bids. Real client reply = 0. Filter pattern at `~/zeroten/audit-scripts/hunter_real_replies.py`; logged at `buglog.jsonl#bug-20260522-0014`

## 2026-05-20 — Day 9 ZERO-TEN cold-start updates (no code change)

Apify Store + repo polish, no behavior changes to the Actor itself.

### Added
- AMA-style `Discussion #16` opened, with a maintainer note covering OAuth setup friction for non-devs and 3 open questions for builders and buyers
- `README.md` badges for the dev.to build-log series, Apify Store build version, and the upstream apify/apify-docs PR
- `Trust signals` footer on both Gumroad listings (Self-Host Bundle $19 PWYW + open-source template $0 PWYW), pointing at source, hosted actor, build log, upstream PR, AMA
- Tutorial article #14 on dev.to with a 5-step refresh-token OAuth walkthrough (Google Cloud Console setup + `dry_run` mode for cold buyers)
- PR opened to upstream: [apify/apify-docs#2549](https://github.com/apify/apify-docs/pull/2549) proposes the refresh-token OAuth tutorial as an official Apify Academy doc
- Comment on [apify/apify-mcp-server#741](https://github.com/apify/apify-mcp-server/issues/741) disambiguating server-level OAuth/SSO (the issue ask) from actor-level credential delegation (this Actor's pattern), with a production reference link

### Changed
- Apify Store category classification: was `[AUTOMATION, DEVELOPER_TOOLS]`, now `[LEAD_GENERATION, AUTOMATION, OPEN_SOURCE]` so the Actor surfaces under the Lead Generation filter where the actual buyer (sales-side freelancer / consultant tracking client follow-ups) is browsing
- Apify Store `exampleRunInput` from placeholder `{ "helloWorld": 123 }` to a real `dry_run: true` input with all three OAuth field placeholders, so the first-touch "Try for free" run shows a meaningful schema

### Fixed
- Article #5 on dev.to (`/7-articles-1-star-0-sales-4-days-...`) had its intro and stats-table header lost during a maintenance PUT that mis-parsed body markdown as YAML frontmatter. Restored a reconstructed intro plus an explicit Editor's note; the Day 6 update tail and Companion list survived. Lesson logged to local `buglog.jsonl#bug-20260520-0007`.



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
