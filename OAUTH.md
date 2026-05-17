# Gmail OAuth Setup — 5 minutes

The Actor needs three things from your own Google Cloud project: `client_id`, `client_secret`, and a `refresh_token`. You generate them once, paste them into the Actor input, and never share your password with anyone.

Why this design: see [Gmail OAuth client_id is not a secret](https://dev.to/foxck016077/gmail-oauth-clientid-is-not-a-secret-a-design-notes-for-self-host-actors-19af).

## Step 1 — Enable the Gmail API

1. Open [console.cloud.google.com](https://console.cloud.google.com)
2. Create a new project (or pick an existing one)
3. Search "Gmail API" in the top bar → **Enable**

## Step 2 — Create OAuth credentials

1. **APIs & Services → Credentials → + Create Credentials → OAuth client ID**
2. If prompted, configure the OAuth consent screen:
   - User type: **External**
   - App name: anything (e.g. `gmail-inbox-intel`)
   - Add yourself as a Test User (Audience → Add users)
   - Scopes: leave empty here, we request `gmail.readonly` from the client
3. Application type: **Desktop app**
4. Name: `gmail-inbox-intel`
5. Click **Create** → copy `client_id` and `client_secret`

## Step 3 — Generate a refresh token

Use [Google's OAuth Playground](https://developers.google.com/oauthplayground):

1. Click the gear icon (top right) → **Use your own OAuth credentials**
2. Paste your `client_id` and `client_secret`
3. Left side: scroll to **Gmail API v1** → check `https://www.googleapis.com/auth/gmail.readonly`
4. **Authorize APIs** → log in with the Google account whose mailbox you want analyzed → grant access
5. **Exchange authorization code for tokens**
6. Copy the `refresh_token` value (starts with `1//`)

## Step 4 — Paste into Actor input

```json
{
  "feature": "reply_metrics",
  "oauth_token": {
    "refresh_token": "1//0g...",
    "client_id": "1234567890-abc.apps.googleusercontent.com",
    "client_secret": "GOCSPX-..."
  },
  "query": "in:inbox newer_than:30d"
}
```

Hit **Save & Start** in the Apify console, or paste this JSON into `apify call foxck/gmail-inbox-intel --input -`.

## What the Actor does with these

- Trades the refresh token for a short-lived access token (in memory, every run)
- Calls Gmail API with `gmail.readonly` scope only
- Returns metadata + reply timing to the dataset
- Never stores your refresh token server-side — Apify holds the input, you control the project

To revoke at any time: [myaccount.google.com/permissions](https://myaccount.google.com/permissions) → find your OAuth app → Remove access.

## Troubleshooting

- **`invalid_grant`** → refresh token expired (90 days of disuse, or you revoked it). Re-run Step 3.
- **`access_denied`** → your Google account is not in the OAuth consent screen's Test Users list. Add it.
- **`Quota exceeded`** → Gmail API per-user limit is 250 units/sec, more than enough for this Actor. If you hit it, you're probably running multiple Actors against the same account.
