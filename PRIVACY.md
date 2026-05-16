# Privacy Policy — Gmail Inbox Intelligence

**Last updated**: 2026-05-15

## TL;DR

This Apify Actor processes your Gmail inbox metadata to produce analytics (thread counts, reply metrics, unread digest, optional summaries). **We do not store your email content on our infrastructure.** All processing happens within Apify platform under your account.

---

## 1. Data We Process

| Data | Purpose | Storage |
|---|---|---|
| OAuth refresh_token / client_id / client_secret | Authenticate to Gmail API | In-memory only, never persisted by Actor code |
| Gmail thread metadata (id, subject, snippet, from, to, date, label) | Compute analytics | Apify Dataset under your Apify account |
| Gmail message body (full content) | Only when `feature=summarizer` enabled | Sent to LLM provider; not stored by Actor |
| OpenAI API key (optional input) | LLM call | In-memory only |
| free_tier_user_id | Quota tracking | Apify KeyValueStore (your account) |

## 2. Data We DO NOT Collect

- Gmail attachments
- Contact lists / address books
- Account credentials beyond OAuth tokens
- IP addresses / location
- Browsing history / device info beyond what Apify platform logs

## 3. Token Handling

- Refresh tokens are accepted as input and used only to exchange for short-lived access tokens within the Actor run
- Access tokens live in memory for the duration of the run
- At end of run, in-memory state is cleared (best effort)
- Log output masks tokens to last 4 chars only

## 4. Third Parties

- **Google Gmail API**: subject to [Google's API Services User Data Policy](https://developers.google.com/terms/api-services-user-data-policy)
- **Apify platform**: subject to [Apify Privacy Policy](https://apify.com/privacy-policy)
- **LLM provider** (optional, only if `enableSummary=true`): your OpenAI key, your terms with OpenAI

## 5. Your Rights

- Delete your data: Apify Dataset and KeyValueStore are under your Apify account; you can delete anytime
- Revoke OAuth: go to [myaccount.google.com](https://myaccount.google.com) → Security → Third-party apps → Revoke
- Stop using: simply stop running the Actor; no recurring billing without active runs

## 6. Compliance

- Limited Use compliance with Google API Services User Data Policy
- No data sold or shared with marketers
- No analytics tracking beyond Apify platform default

## 7. Contact

For privacy questions or data deletion: [Fox 上架時填入 email]

Last reviewed: 2026-05-15
