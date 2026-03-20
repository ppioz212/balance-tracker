"""Entry point — orchestrates fetch → report → notify."""

import sys

from report import generate_report
from notify import send_email
import config


def main() -> None:
    print("Generating finance report...")
    html = generate_report()
    print("Report generated → output/index.html")

    if config.EMAIL_TO and config.GMAIL_APP_PASSWORD:
        print("Sending email digest...")
        send_email(html)
    else:
        print("Email not configured — skipping. Set EMAIL_TO in config.py and GMAIL_APP_PASSWORD env var.")

    print("Done.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
