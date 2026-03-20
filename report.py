"""Takes raw data, applies business logic, renders HTML via Jinja2."""

from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

import config
import fetch


def gather_data() -> dict:
    """Fetch all data and apply business logic.

    Returns a dict ready for template rendering:
        {
            "bank_accounts": [...],
            "credit_cards": [...],
            "report_title": str,
            "generated_at": str,
        }
    """
    bank_accounts = []
    credit_cards = []

    for bank_name, access_token in config.TELLER_ACCESS_TOKENS.items():
        accounts = fetch.fetch_accounts(access_token)

        for acct in accounts:
            if acct["type"] == "depository":
                # Bank accounts: always report, even if zero
                bank_accounts.append({
                    "name": acct["name"],
                    "institution": bank_name,
                    "subtype": acct["subtype"],
                    "balance": acct["balance_current"],
                    "available": acct["balance_available"],
                })

            elif acct["type"] == "credit":
                # Credit cards: skip if balance is zero
                balance = acct["balance_current"]
                if balance == 0:
                    continue

                # Fetch recent transactions for non-zero cards
                transactions = fetch.fetch_transactions(
                    acct["account_id"],
                    access_token,
                    count=config.RECENT_TRANSACTION_COUNT,
                )

                # Flag large purchases
                for txn in transactions:
                    txn["is_large"] = abs(txn["amount"]) >= config.LARGE_PURCHASE_THRESHOLD

                credit_cards.append({
                    "name": acct["name"],
                    "institution": bank_name,
                    "balance": balance,
                    "transactions": transactions,
                })

    return {
        "bank_accounts": bank_accounts,
        "credit_cards": credit_cards,
        "report_title": config.REPORT_TITLE,
        "generated_at": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        "large_purchase_threshold": config.LARGE_PURCHASE_THRESHOLD,
    }


def render_html(data: dict) -> str:
    """Render the report HTML from gathered data."""
    templates_dir = Path(__file__).parent / "templates"
    env = Environment(loader=FileSystemLoader(str(templates_dir)))
    template = env.get_template("report.html")
    return template.render(**data)


def generate_report() -> str:
    """Full pipeline: gather data → render HTML. Returns the HTML string."""
    data = gather_data()
    html = render_html(data)

    # Write to output/index.html
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "index.html"
    output_file.write_text(html)

    return html
