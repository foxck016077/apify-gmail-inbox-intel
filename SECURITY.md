# Security Policy

## Supported versions

Only the `main` branch and the most recent tagged release are actively patched. Older releases will not get security updates.

| Version | Supported |
|---|---|
| main | yes |
| latest tagged release | yes |
| older releases | no |

## Reporting a vulnerability

This Actor handles OAuth refresh tokens and reads users' Gmail metadata. Please report security issues privately, not in a public GitHub issue.

**Preferred channel**: open a [private security advisory](https://github.com/foxck016077/apify-gmail-inbox-intel/security/advisories/new) on this repo. GitHub will keep the report private and coordinated.

**Fallback**: open a regular issue with the title `[security] please contact me privately` and no detail — the maintainer will reach out by another channel.

Please include:

- Reproduction steps (redact your own tokens)
- The feature involved (`thread_search` / `reply_metrics` / `summarizer` / `unread_digest`)
- The version (commit hash) where you observed the issue
- Suggested fix or mitigation if you have one

## Response time

This is a single-maintainer project. Expect:

- Acknowledgement within 72 hours
- Initial triage within 7 days
- Patch ETA depends on severity, but high-severity issues will not be left unpatched for more than 30 days

If a report is critical and you do not get acknowledgement, please escalate via [GitHub Discussions](https://github.com/foxck016077/apify-gmail-inbox-intel/discussions) (publicly visible — say only "I sent a private security report on $DATE, no acknowledgement", no detail).

## Out of scope

- Issues that require an attacker to already have your refresh token. Refresh tokens are sensitive credentials — protect them like passwords.
- Issues in upstream dependencies (`apify`, `google-api-python-client`, `openai`). Report those to their respective maintainers and we will follow the upstream fix.
- Theoretical concerns about OAuth `client_id` visibility — see the [design notes post](https://dev.to/foxck016077/gmail-oauth-clientid-is-not-a-secret-a-design-notes-for-self-host-actors-19af) for why `client_id` is not treated as a secret.

## Coordinated disclosure

If you would like to coordinate public disclosure timing, say so in the private advisory. Standard offer is 90 days from acknowledgement, adjustable for severity and patch readiness.

Thanks for helping keep this Actor safe.
