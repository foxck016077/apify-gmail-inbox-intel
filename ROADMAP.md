# Roadmap

What's coming next, in rough priority order. Anything on this list is a candidate, not a commitment — happy to re-prioritize based on real user feedback in [Discussions](https://github.com/foxck016077/apify-gmail-inbox-intel/discussions).

## Near-term (next 4 weeks)

- **Apify Store publish** — listing draft is in `STORE_LISTING.md`, blocked on cover image + review.
- **Cover image** — needed for Apify Store; not just a hero, also the marketplace card.
- **`thread_search` pagination edge cases** — empty `nextPageToken` after partial result.
- **Per-tenant `kvs` namespace prefix** — useful for multi-account dev setups without rebuilding the Actor.
- **More integration examples** — n8n / Make.com webhook receivers downstream of a scheduled `unread_digest` run.

## Mid-term (1–3 months)

- **Label-aware quota** — count `summarizer` runs separately by label set so heavy-label users don't crowd light ones.
- **Optional Postgres mode** — for users running this on a large team where `KeyValueStore` reset semantics aren't enough.
- **CLI helper** — `python -m gmail_inbox_intel --feature reply_metrics --query "in:inbox"` for local dev outside Apify.
- **Slack / Discord delivery adapter** — opt-in plug for daily digest delivery without writing your own glue.

## Speculative / community-driven

- **Local-LLM summary** — replace OpenAI dependency with Ollama / llama.cpp for users who don't want a third-party LLM in the loop.
- **Reply-suggestion module** — *opt-in only*, never sends, just drafts. Scope expansion needs careful privacy review.
- **Read-only thread export** — `.eml` / `.mbox` snapshots for offline analysis, with explicit per-thread consent.

## Out of scope (explicitly)

To keep the threat model honest and the scope tight:

- **No bulk sending.** This Actor will never grow a send path.
- **No mailbox archival on Apify side.** Every run uses your own OAuth, no cached mailbox dumps.
- **No full-content scraping.** `gmail.readonly` only; no plans to broaden scope.

Disagree? Open a [Discussion](https://github.com/foxck016077/apify-gmail-inbox-intel/discussions) — I'd rather argue the trade-off in the open.
