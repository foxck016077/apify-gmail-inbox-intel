<p align="center">
  <img src=".actor/icon.png" alt="Gmail Inbox Intelligence" width="120" height="120" />
</p>

<h1 align="center">Gmail Inbox Intelligence</h1>

<p align="center"><strong>You're losing deals you didn't know were dying.</strong></p>

<p align="center">Friday triage list of stalled Gmail client threads ranked by SLA breach age. gmail.readonly only, no scraper, no bulk sender, no mailbox stored.</p>

<p align="center">
  <strong>$0 open template</strong> · 
  <a href="https://foxck.gumroad.com/l/freelancer-gmail-tracking-pack"><strong>$19 self-host bundle</strong></a> · 
  <strong>$99 done-for-you triage report</strong> (email me after Gumroad purchase, subject "DFY Triage") · <a href="https://gist.github.com/foxck016077/a21454f7bb4f04d3550b0a606712f293">sample report preview</a>
</p>

<p align="center">
  <a href="https://github.com/foxck016077/apify-gmail-inbox-intel/actions/workflows/test.yml"><img src="https://github.com/foxck016077/apify-gmail-inbox-intel/actions/workflows/test.yml/badge.svg" alt="test" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT" /></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+" /></a>
  <a href="#privacy--oauth"><img src="https://img.shields.io/badge/OAuth-refresh--token--only-green.svg" alt="OAuth: refresh-token-only" /></a>
  <a href="https://developers.google.com/gmail/api/auth/scopes"><img src="https://img.shields.io/badge/Gmail%20scope-readonly-blue.svg" alt="Scope: gmail.readonly" /></a>
  <a href="https://dev.to/foxck016077/series/39853"><img src="https://img.shields.io/badge/dev.to-16%20build--log%20posts-black?logo=devdotto" alt="dev.to series" /></a>
  <a href="https://apify.com/foxck/gmail-inbox-intel"><img src="https://img.shields.io/badge/Apify%20Store-0.1.38-orange" alt="Apify Store build 0.1.38" /></a>
  <a href="https://dev.to/foxck016077/day-16-51-reader-spike-in-85-min-on-devto-0-sales-heres-what-actually-moved-4hc3"><img src="https://img.shields.io/badge/Day%2016-245%20readers%20%2F%200%20sales-red" alt="Day 16 receipts" /></a>
  <a href="https://github.com/apify/apify-docs/pull/2549"><img src="https://img.shields.io/badge/upstream-apify%2Fapify--docs%232549-blue" alt="Upstream PR apify/apify-docs#2549" /></a>
</p>

<p align="center">
  <img src=".actor/screenshot-output.png" alt="reply_metrics output preview — synthetic demo data" width="720" />
</p>

A free, MIT-licensed [Apify Actor](https://apify.com/actors) for Gmail inbox workflow analytics — thread search, reply tracking, LLM summary, unread digest. Built on `gmail.readonly` OAuth scope. **Not a scraper, not a bulk sender, not a mailbox archiver.**

## Build-in-public status (2026-05-22, Day 16)

```
days shipped:        16
dev.to articles:     21
dev.to readers/wk:   245
dev.to followers:    0
Gumroad sales:       0
Apify Actor runs:    8  (0 external users)
GitHub stars:        1  (thank you @kuerdy)
```

Every number is live and honest. Latest post-mortem: [Day 16 — +51 reader spike in 85 min, 0 sales, here's what actually moved](https://dev.to/foxck016077/day-16-51-reader-spike-in-85-min-on-devto-0-sales-heres-what-actually-moved-4hc3). This README updates daily. If anything below looks rotten or out of date, file an issue and I'll fix it.

## Who this is for

- **Solo consultants / freelancers** — get a Friday triage list of client emails that went cold, ranked by how many days past your SLA the thread has been silent.
- **Indie founders running sales by hand** — track which prospects you replied to last and which proposals are quietly dying.
- **Devs building inbox automations** — use the Actor as a Gmail-API building block (refresh-token OAuth, per-feature quota in KVS, async router) for downstream tools.

## Sample output (`reply_metrics`)

```json
{
  "thread_id": "18c4f...",
  "last_message_at": "2026-04-28T09:14:00Z",
  "days_since_last_reply": 9.2,
  "over_sla": true,
  "priority_band": "HOT",
  "reply_chain_length": 4,
  "sender_domain": "acme.com"
}
```

The summary block tells you `priority_breakdown: {HOT: 3, WARM: 5, COLD: 12}` for an at-a-glance Friday triage:

- **HOT** — past SLA but recent (ratio < 1.5×). Standard polite bump still works.
- **WARM** — well past SLA (1.5× to 3×). Needs context refresh, not just a ping.
- **COLD** — deep stale (3×+). Use `reengage_angle` for fresh-news re-entry.

See [`examples/05_dry_run_test.json`](examples/05_dry_run_test.json) for a full synthetic run.

## 30-second start

0. **See the sample output first (anon, no signup)** — open [the Friday Triage gist](https://gist.github.com/foxck016077/a21454f7bb4f04d3550b0a606712f293) — anonymized 10-thread HOT / WARM / COLD output, the exact shape you'd get back. Open in any browser, no login required. Decide whether the *output* is worth the *execution setup* before signing up anywhere.
1. **Run the Actor yourself** — open [apify.com/foxck/gmail-inbox-intel](https://apify.com/foxck/gmail-inbox-intel) (requires a free Apify account — that's the friction layer I caught myself overselling earlier), tick the "Try demo (no OAuth needed)" checkbox, hit Run. You'll see a synthetic 5-thread sample in ~7 seconds.
2. **Want real data?** Paste 3 OAuth fields (`refresh_token`, `client_id`, `client_secret`) — see [OAUTH.md](OAUTH.md) for the 5-minute Google Cloud setup, untick `dry_run`, hit Run again.
3. **Read the dataset** — for `reply_metrics`, you get stalled threads ranked by SLA breach age, ready to paste into Friday triage

No subscription. No server-side mailbox cache. The Actor runs against the official Gmail API in `readonly` scope and exits.

**Want to see the output shape without setting up OAuth?** Set `"dry_run": true` in the input and the Actor skips Gmail entirely, emitting a 3-row synthetic dataset per feature so you can wire up downstream tooling first. See [`examples/05_dry_run_test.json`](examples/05_dry_run_test.json) or this sample run: [Apify console run JnZVfjPrexOfeoSdF](https://console.apify.com/actors/w1viWQDuCUooRYfzk/runs/88ZYxNKtcKiReuDET).

## Also from this shop

The 10 Gumroad listings on [foxck.gumroad.com](https://foxck.gumroad.com/) were all refreshed on Day 16 with the same build-in-public log block — every claim has a date and a number. The most adjacent to this Actor:

- **[Claude Code Mastery: The Reverse-Engineering Guide](https://foxck.gumroad.com/l/claude-code-mastery)** ($49) — every env var, hook event, settings key extracted from the Claude Code v2.1.90 binary. Tested across 13 production services. The internals doc the official docs don't ship.
- **[AI Lead Auto-Responder](https://foxck.gumroad.com/l/ai-lead-responder)** ($39) — n8n template that pairs with this Actor: this Actor scans the inbox, the Auto-Responder handles outbound replies.
- **[5 n8n Workflows that Save 10+ Hours/Week](https://foxck.gumroad.com/l/n8n-smb-automation-pack)** ($29) — the bundle of 5 production-tested templates (lead reply, competitor scan, RSS pipeline, invoice follow-up, review drip).

⭐ **First stargazer:** thanks [@kuerdy](https://github.com/kuerdy) for the cold-start vote of confidence on 2026-05-18. First organic GitHub signal across the whole launch. If you have a Gmail-as-CRM question or just want to compare cold-start notes, the [AMA discussion](https://github.com/foxck016077/apify-gmail-inbox-intel/discussions/16) has your name on it.

📖 Design notes + build log on dev.to — [**ZERO-TEN cold-start build log (16 posts)**](https://dev.to/foxck016077/series/39853):
- [Apify Actor for Gmail inbox analytics: refresh-token-only OAuth, async router, per-feature quota](https://dev.to/foxck016077/an-apify-actor-for-gmail-inbox-analytics-a-refresh-token-only-oauth-async-router-per-feature-pi2)
- [Gmail OAuth client_id is not a secret — design notes for self-host Actors](https://dev.to/foxck016077/gmail-oauth-clientid-is-not-a-secret-a-design-notes-for-self-host-actors-19af)
- [Why refresh-token-only OAuth for a multi-tenant Apify Actor](https://dev.to/foxck016077/why-i-picked-refresh-token-only-oauth-for-a-multi-tenant-apify-actor-265c)
- [Per-feature quota in Apify KeyValueStore — no DB, no cron, no drift](https://dev.to/foxck016077/per-feature-quota-in-apify-keyvaluestore-no-db-no-cron-no-drift-36p4)
- [Open-sourcing an MIT Apify Actor in 24 hours — a build log](https://dev.to/foxck016077/open-sourcing-an-mit-apify-actor-in-24-hours-a-build-log-53km)
- [Apify Actor pricing patterns: Free tier + Pro + Pay-per-result](https://dev.to/foxck016077/apify-actor-pricing-patterns-free-tier-pro-pay-per-result-designing-for-indie-buyers-4e4l)
- [Spinning a $9 PDF off a $0 open-source actor in 4 hours — a build log](https://dev.to/foxck016077/spinning-a-9-pdf-off-a-0-open-source-actor-in-4-hours-a-build-log-2k7i)
- [7 articles, 1 star, 0 sales, 4 days — what an MIT open-source Apify Actor cold start actually looks like](https://dev.to/foxck016077/7-articles-1-star-0-sales-4-days-what-an-mit-open-source-apify-actor-cold-start-actually-looks-j7l)
- [Cold start day 6 — switching the $9 PDF to pay-what-you-want and opening 30% affiliate](https://dev.to/foxck016077/cold-start-day-6-switching-the-9-pdf-to-pay-what-you-want-and-opening-30-affiliate-37im)
- [Day 7 — funnel audit found 7 of 9 articles had no buy link, then I pivoted the product](https://dev.to/foxck016077/day-7-funnel-audit-found-7-of-9-articles-had-no-buy-link-then-i-pivoted-the-product-10ci)
- [Day 8 — I scraped 5 freelance Gumroad top sellers. All 5 wrote one thing I didn't.](https://dev.to/foxck016077/day-8-i-scraped-5-freelance-gumroad-top-sellers-all-5-wrote-one-thing-i-didnt-4o0) (outcome-first vs problem-first hook hypothesis)
- [Day 9 — a 41k-follower Douyin AI-agent creator showed me what I'm missing](https://dev.to/foxck016077/day-9-a-41k-follower-douyin-ai-agent-creator-showed-me-what-im-missing-e3c)
- [Day 9 — PWYW vs $99 lifetime: a back-of-envelope answer to @tokidigital's pricing question](https://dev.to/foxck016077/pwyw-vs-99-lifetime-a-back-of-envelope-answer-to-tokidigitals-pricing-question-5ebl)
- **[Day 9 — How to set up refresh-token-only OAuth for a multi-tenant Apify Actor (Gmail, 10 minutes)](https://dev.to/foxck016077/how-to-set-up-refresh-token-only-oauth-for-a-multi-tenant-apify-actor-gmail-10-minutes-2l6l)** (reader-centric tutorial; PR'd upstream to [apify/apify-docs#2549](https://github.com/apify/apify-docs/pull/2549))
- [Day 10 — I almost sunset my $10 push. Then I checked the demand-source first.](https://dev.to/foxck016077/day-10-i-almost-sunset-my-10-push-then-i-checked-the-demand-source-first-1l0p)
- [Day 11 — pushed 6 outbound surfaces in 30 minutes. Here's what bounced.](https://dev.to/foxck016077/day-11-pushed-6-outbound-surfaces-in-30-minutes-heres-what-bounced-3hjm)
- **[Day 12 — 11 days, 1 user. I think the OAuth field killed the funnel.](https://dev.to/foxck016077/day-12-build-in-public-11-days-1-user-i-think-the-oauth-field-killed-the-funnel-286a)** (post-mortem → build 0.1.36 demo prefill)
- [Day 13 — I claimed '7/7 cover images backfilled.' I checked. Only 1/12 actually had one.](https://dev.to/foxck016077/day-13-i-claimed-77-cover-images-backfilled-i-checked-only-112-actually-had-one-303i) (confession layer 2)
- [Day 14 — 184 reader, 3:21 avg read, 0 new followers, 0 sales](https://dev.to/foxck016077/day-14-184-reader-321-avg-read-time-0-new-followers-0-sales-1457) (7-day dev.to analytics, what compounds vs what doesn't)

📊 **[13-day raw data dump](https://gist.github.com/foxck016077/18621168173229819e367fa71a6144ab)** — every shipped surface, every engagement number, every audit finding in one gist. No narrative, just the numbers.

💬 [Discussions](https://github.com/foxck016077/apify-gmail-inbox-intel/discussions) — design questions, roadmap, open trade-offs.
🙋 [**AMA thread is open**](https://github.com/foxck016077/apify-gmail-inbox-intel/discussions/16) — ask anything about Gmail-as-CRM, stalled-thread scoring, refresh-token OAuth, KVS quota patterns. Answers go back into the docs.
🗺️ [Roadmap](ROADMAP.md) — what's planned, what's speculative, what's explicitly out of scope.
📝 [Changelog](CHANGELOG.md) — what changed in each release.
💝 [Gumroad listing](https://foxck.gumroad.com/l/apify-gmail-inbox-intel) — pay-what-you-want download + email updates when new releases ship.

> **Want to self-host this Actor?** Bundle the full source + `docker-compose.yml` + OAuth setup script + docs into one PWYW download:
> **[Gmail Inbox Intel — Self-Host Bundle](https://foxck.gumroad.com/l/freelancer-gmail-tracking-pack)** — Apify Actor source (Python 3.11, MIT), Docker Compose stack, 5-minute OAuth setup, local KVS storage, no Apify cloud lock-in. Same listing also bundles the original Freelancer Gmail Tracking Pack (30 labels + 12 filters + 5 email templates + Apps Script + 26-page PREMIUM bundle PDF) as a bonus. Pay what you want from $5, suggested $19. 30% affiliate at [foxck.gumroad.com/affiliates](https://foxck.gumroad.com/affiliates).

## Features

- **`thread_search`** — search Gmail threads by query, paginate, return metadata + message counts
- **`reply_metrics`** — for each thread, compute reply-from-me / reply-from-others / last reply age / SLA breach flag
- **`summarizer`** — optional OpenAI LLM thread summary (you supply your own API key)
- **`unread_digest`** — list unread threads in last N hours, grouped by label
- **`reengage_angle`** — for each cold/over-SLA thread, fetch recent Google News headlines about the counterparty company so you re-enter with new context, not a "just circling back" reminder. Optional `openai_api_key` adds an LLM layer that drafts 3 short re-engage email options grounded in those news items. Grounded in two buyer-voice anchors: [r/sales 1tdngew](https://www.reddit.com/r/sales/comments/1tdngew/) (49 comments, 12 mentions of "new context / what changed" as the actual re-engage demand) and [r/smallbusiness 1td0827](https://www.reddit.com/r/smallbusiness/comments/1td0827/) (60 comments, top reply at 61 score: *"holding 50 open loops in your head ... move the memory of the business out of your head"* — the small-biz-owner variant of the same demand). No API key required for the headlines layer. **[Worked example walkthrough →](docs/EXAMPLE_REENGAGE_WALKTHROUGH.md)**

## Use Cases

- **Freelancer Friday triage**: `reply_metrics` against `from:client-domains newer_than:21d`, sort by `last_reply_age_days desc`, send Day-3/7/14 bumps to anything past the threshold. Replaces a CRM if you have < 50 active threads.
- **Sales / BD pipeline rot**: `reply_metrics` against `label:outbound` weekly, alert when `reply_from_other` is empty 14d+. Cheaper than HubSpot for a small list.
- **PM / Ops morning digest**: `unread_digest` against the last 12h grouped by `label`. Cron from Apify schedule → email yourself the dataset URL.
- **Personal weekly review**: `thread_search` for `is:starred OR label:important newer_than:7d` → triage backlog without forwarding emails to a third party.

## Privacy & OAuth

- You provide your own OAuth credentials in Actor input (`refresh_token` + `client_id` + `client_secret`)
- Refresh-token-only flow — Actor exchanges for short-lived access token in memory each run
- Job-end state is cleared (best effort)
- **We never store your Gmail.** Every run uses your own OAuth, no server-side mailbox cache.

## Pricing

**Free.** MIT licensed. Run it on Apify (their compute-unit pricing applies — usually pennies per run) or fork and run on your own box.

The repo includes a `free_tier_user_id` quota hook for future-self if you want to wrap it as a paid SaaS, but no billing layer ships with this Actor. If you'd rather pay for a setup instead of self-hosting OAuth, the [PWYW $1+ manual companion pack](https://foxck.gumroad.com/l/freelancer-gmail-tracking-pack) (now includes a 26-page bundle PDF) skips OAuth entirely.

## Input Schema (13 fields)

| Field | Type | Required | Notes |
|---|---|---|---|
| `feature` | enum | yes | `thread_search` / `reply_metrics` / `summarizer` / `unread_digest` / `reengage_angle` |
| `oauth_token` | object | yes | `{refresh_token, client_id, client_secret}` |
| `query` | string | no | Gmail search query (default `in:inbox`) |
| `max_results` | integer | no | default 50, max 500 |
| `sla_days` | integer | no | default 14, for `reply_metrics` + `reengage_angle` |
| `from_domains` | string[] | no | sender-domain whitelist for `reply_metrics` |
| `include_reengage_angles` | boolean | no | default false; when true, `reply_metrics` returns news angles inline |
| `news_lookback_days` | integer | no | default 90, range 7-365 |
| `max_news_per_thread` | integer | no | default 5, range 1-20 |
| `openai_api_key` | string | no | optional LLM key for `summarizer` and `reengage_angle` email-draft layer |
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

Browsing the Apify ecosystem? See [**awesome-apify-actors**](https://github.com/foxck016077/awesome-apify-actors) — a curated list of 68+ production Apify Actors across 16 categories (Scrapers, Search, Maps, Social media, Lead gen, Email). This Actor is listed under *Email & Productivity*.

Looking for ready-to-import Gmail / AI / n8n templates? Some Gumroad workflows that pair well with this Actor:

- **AI Lead Auto-Responder** — Gmail → AI replies n8n workflow: https://foxck.gumroad.com/l/ai-lead-responder
- **AI Content Pipeline** — RSS → Social Media n8n template: https://foxck.gumroad.com/l/ai-content-pipeline
- **Competitor Monitor** — Daily AI analysis + weekly reports n8n: https://foxck.gumroad.com/l/competitor-monitor
- **Claude Code Mastery** — practical playbook for Claude Code workflows: https://foxck.gumroad.com/l/claude-code-mastery

Full catalog: https://foxck.gumroad.com

## Roadmap

### v0.2 — Web wrapper for non-developers (OAuth wired, awaiting Cloud Console setup)

The Apify Actor today targets builders comfortable with OAuth `client_secrets` and `INPUT.json`. `v0.2` is a hosted web app aimed at sales-side freelancers and consultants who want the same stalled-thread output without running Actors themselves:

- One-click Google sign-in via NextAuth v5 + `gmail.readonly` scope only — **code wired**
- Inbox table sorted by days silent, CSV download — **shipped in preview**
- `refresh_token` lives only on the server-side JWT, never on disk or in a database
- Same read-only positioning, no outbound automation

**Preview repo**: [`foxck016077/gmail-inbox-web`](https://github.com/foxck016077/gmail-inbox-web) — Next.js 16 + React 19 + Tailwind v4 + TypeScript. NextAuth + Gmail API integration is in commit `256d2c8`. The only thing standing between the current repo and live sign-in is the one-time Google Cloud Console OAuth client registration plus 3 env vars on Vercel.

Existing competitor landscape (verified 2026-05-20): Mailbutler ($4–$11/mo, tracking + signatures), Boomerang (snooze + scheduled send), Streak / Mixmax / Instantly ($15–$59/mo, Gmail CRM + mass outbound). No current player covers stalled-thread visualization as a read-only inbox health view. That gap is what `v0.2` targets.

Have an opinion on what `v0.2` should look like before it ships? Open [Discussion #16](https://github.com/foxck016077/apify-gmail-inbox-intel/discussions/16).

## License

MIT — see `LICENSE`.
