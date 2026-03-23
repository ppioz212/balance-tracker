# Balance Tracker

Personal finance tracker that fetches credit card and bank account data via the Teller.io API, generates an HTML report, and sends a daily email digest.

## Architecture

- `fetch.py` — All Teller API calls (mTLS + access token auth via `requests`)
- `report.py` — Gathers data, applies business logic, renders HTML via Jinja2
- `notify.py` — Sends email via Gmail SMTP (smtplib)
- `config.py` — All tunable values, reads secrets from environment variables
- `run.py` — Entry point: fetch → report → notify
- `setup_teller.py` — One-time local script to enroll a bank via Teller Connect and get an access token
- `templates/report.html` — Jinja2 template styled with Tailwind CDN

## Multi-bank support

Each bank gets its own env var: `TELLER_ACCESS_TOKEN_<BANK>` (e.g. `TELLER_ACCESS_TOKEN_CHASE`). Config auto-discovers all matching env vars. To add a new bank, run `setup_teller.py`, get the token, and add a new secret.

## Business logic

- Bank accounts: always shown, even if zero balance
- Credit cards: skipped entirely if balance is zero
- Transactions over `LARGE_PURCHASE_THRESHOLD` ($100) are flagged with an amber indicator
- Last 5 transactions shown per non-zero credit card

## Running locally

```bash
source .env    # contains access tokens, email, gmail app password
python3 run.py
```

The `.env` file and `.pem` certificate files are gitignored.

## GitHub Actions

- Workflow: `.github/workflows/daily.yml`
- Cron is currently **disabled** (commented out) — manual trigger only via `workflow_dispatch`
- Uncomment the schedule lines to enable daily runs at 7am EST

### Required secrets

| Secret | Purpose |
|---|---|
| `TELLER_ACCESS_TOKEN_CHASE` | Teller access token for Chase |
| `TELLER_CERT` | Base64-encoded certificate.pem |
| `TELLER_KEY` | Base64-encoded private_key.pem |
| `EMAIL_TO` | Recipient email address |
| `EMAIL_FROM` | Sender Gmail address |
| `GMAIL_APP_PASSWORD` | Gmail app password for SMTP |

## Teller.io specifics

- Auth: mTLS (client cert + private key) + access token via HTTP Basic Auth
- No Python SDK — uses `requests` with `cert=` and `auth=` params
- API base: `https://api.teller.io`
- Amounts and balances come back as strings from the API, converted to floats in fetch.py
- Certificate/key files downloaded from Teller dashboard as a zip
