# Apify Store Listing — Fill-in Pack

Drop these into Apify Console > Actor > Publish > Store listing tab.

Pricing rationale and copy are drafts based on competitor scan (no other Gmail-readonly Apify Actor at the time of writing). Adjust before publish.

---

## Title (max 50 chars)

`Gmail Inbox Intelligence`

## Subtitle / short description (max 150 chars)

`Search threads, track replies, summarize, and get unread digests for your own Gmail — read-only, your OAuth, no server-side mailbox cache.`

## Categories (Apify allows 1–3)

Suggested: `BUSINESS`, `AUTOMATION`, `PRODUCTIVITY`

Fallback if Apify renames: pick the closest to "office automation" / "inbox tools".

## Long description (paste into the rich-text editor)

This Actor turns your own Gmail inbox into a structured signal source — without forwarding emails anywhere, without bulk sending, and without storing a copy of your mailbox.

**Four features in one Actor (pick one per run via the `feature` input):**

- `thread_search` — search Gmail threads with full Gmail query syntax, return paginated metadata and message counts.
- `reply_metrics` — for each thread compute reply-from-me / reply-from-others / last reply age / SLA breach flag. Useful to surface stalled outbound threads.
- `summarizer` — optional thread summary via your own OpenAI API key (model defaults to `gpt-4o-mini`).
- `unread_digest` — list unread threads in the last N hours, grouped by Gmail label.

**Built for read-only operation.** The Actor uses `gmail.readonly` scope and refresh-token-only OAuth. You bring your own OAuth credentials (`refresh_token`, `client_id`, `client_secret`). Access tokens are exchanged in-memory each run. There is no server-side mailbox cache.

**Who this is for:**

- Freelancers tracking which client threads have not replied yet.
- Sales / BD watching stalled outbound threads before they go cold.
- PMs and ops folks who want a morning unread digest grouped by project label.
- Anyone running a weekly inbox audit without manual filtering.

**Privacy posture:** least-privilege scope (`gmail.readonly`), no write/send access, no third-party storage of mail content. Per-feature quota slots prevent a runaway job from blowing up an entire day's allowance.

**Open source under MIT** — see the GitHub repo for design notes, including refresh-token-only rationale and multi-tenant key-naming choices.

## Pricing model

**Recommended: Monthly + pay-per-result combo**

- Monthly subscription: $19 / month (5,000 thread metadata reads + 100 LLM summaries)
- Pay-per-result add-on: $0.50 per 1,000 thread metadata; $0.005 per summary
- Free tier: 100 threads / month (KVS-quota tracked)

**Rationale:** monthly anchors revenue; pay-per-result lets heavy users scale without overage friction. Free tier keeps cold-start signup possible.

**Alternative (simpler):** flat pay-per-result only — $0.001 per thread metadata, $0.01 per summary. Easier to communicate, lower ceiling.

Pick one and stick with it for at least 30 days before adjusting.

## Min Apify plan

`Starter` (most users should already have this — Free plan can run for testing).

## Example input (paste into the Example tab)

```json
{
  "feature": "unread_digest",
  "oauth_token": {
    "refresh_token": "1//0gAAAA...redacted",
    "client_id": "1234567890.apps.googleusercontent.com",
    "client_secret": "GOCSPX-redacted"
  },
  "max_results": 50,
  "dry_run": false
}
```

For `summarizer` feature, also pass `openai_api_key` and optionally `summary_model`.

## Tags (search keywords)

`gmail` `inbox` `oauth` `automation` `productivity` `email-analytics` `workflow` `unread-digest` `reply-tracking` `python`

## Repository URL

https://github.com/foxck016077/apify-gmail-inbox-intel

## Support URL

GitHub Discussions: https://github.com/foxck016077/apify-gmail-inbox-intel/discussions

## Pre-publish checklist

- [ ] OAuth credentials redacted in example input
- [ ] Pricing model decided (monthly+ppa OR flat ppr)
- [ ] Icon (.actor/icon.png) verified 512×512 or larger
- [ ] Screenshots (.actor/screenshot-input.png + screenshot-output.png) verified
- [ ] README.md `Pricing` section matches Store listing
- [ ] LICENSE = MIT (already in repo)
- [ ] Repo is public (already)
- [ ] At least 1 successful test run in your Apify account
