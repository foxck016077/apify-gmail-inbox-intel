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

The `reengage_angle` feature was built specifically against the buyer voice in [r/sales 1tdngew](https://www.reddit.com/r/sales/comments/1tdngew/), where 12 of 25 substantive comments said the same thing:

> "re-enter with new context, not reminders"

> "always come back with something NEW"

> "Lead with what changed, not with a check in"

The most-upvoted answer (33 upvotes) was Only_Walk_3740: "re-enter with new context, not reminders... share something relevant, then ask a simple, low pressure question that resets conversation."

The feature literally does that — `suggested_angles` is the "what changed" surface, `draft_emails` is the LLM-drafted re-entry option. The user picks; the actor proposes.

## Pricing fit

- **$0** open-source actor (this) — for users who already have an Apify account and want to run it themselves
- **$19** [self-host bundle](https://foxck.gumroad.com/l/freelancer-gmail-tracking-pack) — Docker Compose, no Apify free-tier limits, runs on your own VPS
- **$99** done-for-you triage — email me after Gumroad purchase, subject `DFY Triage`. I run the scan on your Gmail (refresh-token OAuth, read-only, never stored), send back a 1-page Friday report within 7 days. First buyer $49. [Sample report preview](https://gist.github.com/foxck016077/a21454f7bb4f04d3550b0a606712f293).

## TAM

This feature targets solo consultants / freelancers / small sales teams with **50–200 active client threads**. If you run high-volume outbound (5k+ emails/month, agency / SDR team), this is not your tool — that audience needs Instantly / Smartlead / Apollo / Prospeo, not inbox-side triage. We checked. We are not pretending to compete with sequencers.
