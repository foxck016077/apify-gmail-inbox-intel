# Examples

Minimal input JSON per feature. Replace OAuth credentials with your own before running.

| File | Feature | Use case |
|---|---|---|
| `01_thread_search_basic.json` | `thread_search` | Find Stripe receipts from the last 30 days |
| `02_reply_metrics_sla.json` | `reply_metrics` | Check which sent threads have not been replied to in 14 days |
| `03_summarizer_openai.json` | `summarizer` | Summarize last 3 days of unread threads (requires OpenAI key) |
| `04_unread_digest_grouped.json` | `unread_digest` | Group unread threads by Gmail label |
| `05_dry_run_test.json` | `thread_search` | No-credentials sanity check (`dry_run: true`) |

## OAuth credential setup

You need three values:

- `refresh_token` — obtained from a one-time OAuth consent flow with `gmail.readonly` scope
- `client_id` — public identifier for your Google Cloud OAuth client
- `client_secret` — private; treat like a password

See the [refresh-token-only design notes](https://dev.to/foxck016077/why-i-picked-refresh-token-only-oauth-for-a-multi-tenant-apify-actor-265c) for why this Actor uses refresh-token-only rather than the 3-legged interactive flow.

## Apify quick start

In Apify Console → your Actor → **Input** tab → paste any of these JSON files → **Save & Start**.

## Local quick start

```bash
cp examples/05_dry_run_test.json input.json
apify run
```

`dry_run: true` skips real Gmail API calls. Useful for verifying installation.
