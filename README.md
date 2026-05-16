# Gmail Inbox Intelligence

[![test](https://github.com/foxck016077/apify-gmail-inbox-intel/actions/workflows/test.yml/badge.svg)](https://github.com/foxck016077/apify-gmail-inbox-intel/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![OAuth: refresh-token-only](https://img.shields.io/badge/OAuth-refresh--token--only-green.svg)](#privacy--oauth)
[![Scope: gmail.readonly](https://img.shields.io/badge/Gmail%20scope-readonly-blue.svg)](https://developers.google.com/gmail/api/auth/scopes)

Apify Actor for Gmail inbox workflow analytics — thread search, reply tracking, LLM summary, unread digest. Built on `gmail.readonly` OAuth scope. **Not a scraper, not a bulk sender.**

📖 Design notes on dev.to — [**series index**](https://dev.to/foxck016077/series/39719):
- [Apify Actor for Gmail inbox analytics: refresh-token-only OAuth, async router, per-feature quota](https://dev.to/foxck016077/an-apify-actor-for-gmail-inbox-analytics-a-refresh-token-only-oauth-async-router-per-feature-pi2)
- [Gmail OAuth client_id is not a secret — design notes for self-host Actors](https://dev.to/foxck016077/gmail-oauth-clientid-is-not-a-secret-a-design-notes-for-self-host-actors-19af)
- [Why refresh-token-only OAuth for a multi-tenant Apify Actor](https://dev.to/foxck016077/why-i-picked-refresh-token-only-oauth-for-a-multi-tenant-apify-actor-265c)
- [Per-feature quota in Apify KeyValueStore — no DB, no cron, no drift](https://dev.to/foxck016077/per-feature-quota-in-apify-keyvaluestore-no-db-no-cron-no-drift-36p4)
- [Open-sourcing an MIT Apify Actor in 24 hours — a build log](https://dev.to/foxck016077/open-sourcing-an-mit-apify-actor-in-24-hours-a-build-log-53km)

💬 [Discussions](https://github.com/foxck016077/apify-gmail-inbox-intel/discussions) — design questions, roadmap, open trade-offs.

## Features

- **`thread_search`** — search Gmail threads by query, paginate, return metadata + message counts
- **`reply_metrics`** — for each thread, compute reply-from-me / reply-from-others / last reply age / SLA breach flag
- **`summarizer`** — optional OpenAI LLM thread summary (you supply your own API key)
- **`unread_digest`** — list unread threads in last N hours, grouped by label

## Use Cases

- **Freelancer**: see which clients haven't replied yet, ranked by SLA breach
- **Sales / BD**: surface stalled outbound threads before they go cold
- **PM / Ops**: morning unread digest grouped by project label
- **Personal**: weekly inbox audit without forwarding emails anywhere

## Privacy & OAuth

- You provide your own OAuth credentials in Actor input (`refresh_token` + `client_id` + `client_secret`)
- Refresh-token-only flow — Actor exchanges for short-lived access token in memory each run
- Job-end state is cleared (best effort)
- **We never store your Gmail.** Every run uses your own OAuth, no server-side mailbox cache.

## Pricing

- **Free**: 100 threads / month
- **Pro**: $19 / month (5000 threads metadata + 100 LLM summaries)
- **Pay-per-result add-on**: $0.50 / 1,000 thread metadata, $0.005 / summary

Payouts via Wise (international).

## Input Schema (8 fields)

| Field | Type | Required | Notes |
|---|---|---|---|
| `feature` | enum | yes | `thread_search` / `reply_metrics` / `summarizer` / `unread_digest` |
| `oauth_token` | object | yes | `{refresh_token, client_id, client_secret}` |
| `query` | string | no | Gmail search query (default `in:inbox`) |
| `max_results` | integer | no | default 50, max 500 |
| `openai_api_key` | string | no | required only for `summarizer` |
| `summary_model` | string | no | default `gpt-4o-mini` |
| `free_tier_user_id` | string | no | for free-tier quota tracking |
| `dry_run` | boolean | no | skip Gmail API calls (test mode) |

See `.actor/INPUT_SCHEMA.json` for full spec, and [`examples/`](examples/) for 5 ready-to-paste input JSON files per feature.

## Local Dev

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest               # 6 tests, asyncio_mode=auto
apify run            # local actor run with .actor/INPUT_SCHEMA.json
```

## Related Projects

Looking for ready-to-import Gmail / AI / n8n templates? Some Gumroad workflows that pair well with this Actor:

- **AI Lead Auto-Responder** — Gmail → AI replies n8n workflow: https://foxck.gumroad.com/l/ai-lead-responder
- **AI Content Pipeline** — RSS → Social Media n8n template: https://foxck.gumroad.com/l/ai-content-pipeline
- **Competitor Monitor** — Daily AI analysis + weekly reports n8n: https://foxck.gumroad.com/l/competitor-monitor
- **Claude Code Mastery** — practical playbook for Claude Code workflows: https://foxck.gumroad.com/l/claude-code-mastery

Full catalog: https://foxck.gumroad.com

## License

MIT — see `LICENSE`.
