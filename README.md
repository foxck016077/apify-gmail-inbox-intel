<p align="center">
  <img src=".actor/icon.png" alt="Gmail Inbox Intelligence" width="120" height="120" />
</p>

<h1 align="center">Gmail Inbox Intelligence</h1>

<p align="center"><strong>Reply tracking, SLA monitoring, and unread digests for your Gmail — without a scraper, without a bulk sender, without storing your mailbox.</strong></p>

<p align="center">
  <a href="https://github.com/foxck016077/apify-gmail-inbox-intel/actions/workflows/test.yml"><img src="https://github.com/foxck016077/apify-gmail-inbox-intel/actions/workflows/test.yml/badge.svg" alt="test" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" /></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+" /></a>
  <a href="#privacy--oauth"><img src="https://img.shields.io/badge/OAuth-refresh--token--only-green.svg" alt="OAuth: refresh-token-only" /></a>
  <a href="https://developers.google.com/gmail/api/auth/scopes"><img src="https://img.shields.io/badge/Gmail%20scope-readonly-blue.svg" alt="Scope: gmail.readonly" /></a>
</p>

<p align="center">
  <img src=".actor/screenshot-output.png" alt="reply_metrics output preview — synthetic demo data" width="720" />
</p>

A self-host-friendly [Apify Actor](https://apify.com/actors) for Gmail inbox workflow analytics — thread search, reply tracking, LLM summary, unread digest. Built on `gmail.readonly` OAuth scope. **Not a scraper, not a bulk sender, not a mailbox archiver.**

📖 Design notes on dev.to — [**series index**](https://dev.to/foxck016077/series/39719):
- [Apify Actor for Gmail inbox analytics: refresh-token-only OAuth, async router, per-feature quota](https://dev.to/foxck016077/an-apify-actor-for-gmail-inbox-analytics-a-refresh-token-only-oauth-async-router-per-feature-pi2)
- [Gmail OAuth client_id is not a secret — design notes for self-host Actors](https://dev.to/foxck016077/gmail-oauth-clientid-is-not-a-secret-a-design-notes-for-self-host-actors-19af)
- [Why refresh-token-only OAuth for a multi-tenant Apify Actor](https://dev.to/foxck016077/why-i-picked-refresh-token-only-oauth-for-a-multi-tenant-apify-actor-265c)
- [Per-feature quota in Apify KeyValueStore — no DB, no cron, no drift](https://dev.to/foxck016077/per-feature-quota-in-apify-keyvaluestore-no-db-no-cron-no-drift-36p4)
- [Open-sourcing an MIT Apify Actor in 24 hours — a build log](https://dev.to/foxck016077/open-sourcing-an-mit-apify-actor-in-24-hours-a-build-log-53km)

💬 [Discussions](https://github.com/foxck016077/apify-gmail-inbox-intel/discussions) — design questions, roadmap, open trade-offs.
🗺️ [Roadmap](ROADMAP.md) — what's planned, what's speculative, what's explicitly out of scope.
📝 [Changelog](CHANGELOG.md) — what changed in each release.
💝 [Gumroad listing](https://foxck.gumroad.com/l/apify-gmail-inbox-intel) — pay-what-you-want download + email updates when new releases ship.

> **Don't want to self-host?** If you have < 50 active client threads, the manual setup is probably easier:
> **[Freelancer Gmail Client Tracking Pack — $9](https://foxck.gumroad.com/l/freelancer-gmail-tracking-pack)** — 30 labels + 12 filters + 5 follow-up email templates + Apps Script. Setup in 20 min, no CRM, no subscription. Same SLA-breach detection, manual version.

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

<p align="center">
  <img src=".actor/screenshot-input.png" alt="Actor input — OAuth fields masked for demo" width="720" />
</p>

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
