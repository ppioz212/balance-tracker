"""All tunable configuration values for the finance tracker."""

import os

# --- Thresholds & Display ---
LARGE_PURCHASE_THRESHOLD = 100  # dollars — transactions above this get flagged
RECENT_TRANSACTION_COUNT = 5    # how many recent transactions to show per card

# --- Email ---
EMAIL_TO = os.environ.get("EMAIL_TO", "")
EMAIL_FROM = os.environ.get("EMAIL_FROM", "")
REPORT_TITLE = "Daily Finance Digest"

# --- Teller ---
# Add a TELLER_ACCESS_TOKEN_<BANK> env var for each enrolled bank
TELLER_ACCESS_TOKENS = {
    name.replace("TELLER_ACCESS_TOKEN_", "").replace("_", " ").title(): value
    for name, value in os.environ.items()
    if name.startswith("TELLER_ACCESS_TOKEN_")
}
TELLER_CERT_PATH = os.environ.get("TELLER_CERT_PATH", "certificate.pem")
TELLER_KEY_PATH = os.environ.get("TELLER_KEY_PATH", "private_key.pem")
TELLER_API_BASE = "https://api.teller.io"

# --- Gmail ---
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
GMAIL_SMTP_SERVER = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587
