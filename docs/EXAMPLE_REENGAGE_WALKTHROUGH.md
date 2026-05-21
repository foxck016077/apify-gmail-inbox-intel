# Worked example: 60 stalled client threads → re-engage angles in 5 minutes

> Concrete walkthrough for the `reengage_angle` feature. Synthetic data for a solo brand-designer freelancer with ~60 active client threads, of which 12 have crossed her 14-day SLA.

## Step 0 — Run the actor

```bash
apify call foxck/gmail-inbox-intel --input '{
  "feature": "reengage_angle",
  "oauth_token": {
    "refresh_token": "<your refresh token>",
    "client_id": "<your OAuth client id>",
    "client_secret": "<your OAuth client secret>"
  },
  "query": "in:inbox -in:sent newer_than:120d",
  "max_results": 100,
  "sla_days": 14,
  "news_lookback_days": 90,
  "max_news_per_thread": 5
}'
```

Add `"openai_api_key": "sk-..."` if you want LLM-drafted email options (uses the same key the existing `summarizer` feature uses).

## Step 1 — Read the summary

```json
{
  "summary": {
    "total_cold_threads": 8,
    "skipped_generic_domain": 4,
    "sla_days_threshold": 14,
    "news_lookback_days": 90
  }
}
```

- `total_cold_threads`: 8 threads crossed the 14-day SLA and the counterparty domain is corporate (skipped 4 personal `@gmail.com` / `@icloud.com` etc).

## Step 2 — Scan one thread output

```json
{
  "thread_id": "189f4...",
  "subject": "Re: Brand refresh — Q3 launch",
  "counterparty_domain": "acme.co",
  "company_search_term": "acme",
  "days_silent": 47.0,
  "reply_chain_length": 4,
  "suggested_angles": [
    {
      "headline": "Acme closes Series B funding led by Sequoia, to expand Asia-Pacific go-to-market",
      "url": "https://techcrunch.com/...",
      "pub_date": "Wed, 14 May 2026 09:00:00 GMT",
      "source": "TechCrunch"
    },
    {
      "headline": "Acme appoints new VP of Brand from Stripe",
      "url": "https://businesswire.com/...",
      "pub_date": "Mon, 12 May 2026 11:30:00 GMT",
      "source": "Business Wire"
    }
  ],
  "draft_emails": [
    {
      "angle": "Series B funding (TechCrunch)",
      "draft": "Hey Maya, saw Acme just closed Series B — congrats. Last time we talked in March you were prioritizing the Q3 brand refresh; with the new runway and the APAC push, did the Q3 timeline stretch or stay the same? Happy to update the scope if priorities shifted. One reply either way and I'll stop chasing."
    },
    {
      "angle": "New VP Brand from Stripe",
      "draft": "Hey Maya, noticed Acme just hired a new VP Brand from Stripe — congrats on the team build. Since the Q3 brand refresh we were scoping touched the same surface, would it make more sense for me to introduce myself to your new VP directly, or is that scope on hold for now?"
    }
  ]
}
```

## Step 3 — What this changes for the user

Without the actor, this freelancer would either:
- Send a generic "just circling back" email and get the standard 0-reply silence
- Not follow up at all because she does not know if the Acme Q3 brand refresh is still alive

With the actor:
- She knows Acme just closed Series B (new context, easy hook)
- She knows there is a new VP Brand who probably has not seen the original thread (re-entry path: introduce to the new owner, not the silent thread)
- She picks one of the two drafted emails, edits it for tone, sends it. 4 sentences max. Low-friction yes/no ask.

## Why this matches buyer voice

Two buyer-voice anchors, both surfaced through Reddit hot-thread caches.

**Anchor 1 — re-engage tactic side**, [r/sales 1tdngew](https://www.reddit.com/r/sales/comments/1tdngew/): 49 comments, 12 of 25 substantive answers said the same thing.

> "re-enter with new context, not reminders"

> "always come back with something NEW"

> "Lead with what changed, not with a check in"

Most-upvoted answer (33 upvotes): "re-enter with new context, not reminders... share something relevant, then ask a simple, low pressure question that resets conversation."

The `suggested_angles` + `draft_emails` output is that pattern in code.

**Anchor 2 — buyer mental load side**, [r/smallbusiness 1td0827](https://www.reddit.com/r/smallbusiness/comments/1td0827/): 60 comments, top reply at 61 score (above the OP).

> "The exhaustion usually stems from the 'switching cost' of jumping between different context layers... your brain is fried from holding 50 open loops in your head to make sure nothing slips through the cracks. The only way to lower that mental load is to move the 'memory' of the business out of your head."

The walkthrough above shows that "move the memory out of your head" pattern in code: 60 threads in the inbox → 8 cold + 4 dormant → 2 drafted emails per dormant thread → solo owner picks one. The buyer no longer has to remember which Acme thread was about Q3 brand refresh vs which was about Q4 ops — the actor reconstructs the context.

## Worked example 2 — small-business owner with 200 supplier threads

Anchor 2 maps to a second buyer persona. Less polished story, same engine:

Imagine Jordan runs a 4-person e-commerce shop. 200 active threads in inbox: suppliers, freight forwarders, ad-platform reps, customer-support escalations, contractor invoices. Jordan's SLA habit is to reply within 5 days but the dormant-thread tail builds up because Jordan forgets which Alibaba supplier sent the latest sample.

```bash
apify call foxck/gmail-inbox-intel --input '{
  "feature": "reengage_angle",
  "oauth_token": {...},
  "query": "in:inbox -in:sent newer_than:180d",
  "sla_days": 7,
  "dormant_days": 60,
  "max_results": 300
}'
```

Output (summarized):

```json
{
  "summary": {
    "total_cold_threads": 22,
    "total_dormant_threads": 11,
    "skipped_generic_domain": 18
  }
}
```

22 cold + 11 dormant = 33 thread re-entries waiting. Jordan does not read 33 drafted emails. Jordan reads the *counts* and decides: "ok, this Friday I'm only touching the 11 dormant ones, the 22 cold can wait one more week." That decision was the 30-second action — without the actor it would have been a 90-minute "Jordan stares at inbox and gets overwhelmed" loop.

That is the "memory out of your head" outcome the r/smallbusiness top-voted reply asked for. The drafted-email layer is optional; the *counts* are the load reduction.

## Alternative workflow — one API call instead of two

If you already use `reply_metrics` to get your stalled-thread list, set `include_reengage_angles: true` and get the news headlines inline on each over-SLA thread:

```bash
apify call foxck/gmail-inbox-intel --input '{
  "feature": "reply_metrics",
  "oauth_token": {...},
  "query": "in:inbox -in:sent newer_than:120d",
  "sla_days": 14,
  "include_reengage_angles": true
}'
```

The `threads_over_sla` array will now have a `suggested_angles` field on each thread, populated with the same Google News headlines that the standalone `reengage_angle` feature returns. One Gmail auth, one OAuth round-trip, one run.

If you don't need news headlines (just the cold-thread list), leave `include_reengage_angles` unset (defaults to `false`). Backward compatible.

## Pricing fit

- **$0** open-source actor (this) — for users who already have an Apify account and want to run it themselves
- **$19** [self-host bundle](https://foxck.gumroad.com/l/freelancer-gmail-tracking-pack) — Docker Compose, no Apify free-tier limits, runs on your own VPS
- **$99** done-for-you triage — email me after Gumroad purchase, subject `DFY Triage`. I run the scan on your Gmail (refresh-token OAuth, read-only, never stored), send back a 1-page Friday report within 7 days. First buyer $49. [Sample report preview](https://gist.github.com/foxck016077/a21454f7bb4f04d3550b0a606712f293).

## TAM

This feature targets solo consultants / freelancers / small sales teams with **50–200 active client threads**. If you run high-volume outbound (5k+ emails/month, agency / SDR team), this is not your tool — that audience needs Instantly / Smartlead / Apollo / Prospeo, not inbox-side triage. We checked. We are not pretending to compete with sequencers.
