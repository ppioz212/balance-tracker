"""All Teller API calls. Returns raw account and transaction data."""

import requests

import config


def _request(endpoint: str, access_token: str) -> dict | list:
    """Make an authenticated request to the Teller API with mTLS."""
    response = requests.get(
        f"{config.TELLER_API_BASE}{endpoint}",
        cert=(config.TELLER_CERT_PATH, config.TELLER_KEY_PATH),
        auth=(access_token, ""),
    )
    response.raise_for_status()
    return response.json()


def fetch_accounts(access_token: str) -> list[dict]:
    """Fetch all linked accounts (bank + credit card) with balances.

    Returns a list of dicts:
        {
            "account_id": str,
            "name": str,
            "type": "depository" | "credit",
            "subtype": "checking" | "savings" | "credit_card" | ...,
            "balance_current": float,
            "balance_available": float | None,
        }
    """
    accounts_raw = _request("/accounts", access_token)
    accounts = []

    for acct in accounts_raw:
        # Fetch balances for each account
        balances = _request(f"/accounts/{acct['id']}/balances", access_token)
        ledger = float(balances["ledger"]) if balances.get("ledger") else 0.0
        available = float(balances["available"]) if balances.get("available") else None

        accounts.append({
            "account_id": acct["id"],
            "name": acct["name"],
            "type": acct["type"],
            "subtype": acct.get("subtype", ""),
            "balance_current": ledger,
            "balance_available": available,
        })

    return accounts


def fetch_transactions(account_id: str, access_token: str, count: int = config.RECENT_TRANSACTION_COUNT) -> list[dict]:
    """Fetch recent transactions for a specific account.

    Returns a list of dicts sorted by date descending:
        {
            "date": str (YYYY-MM-DD),
            "merchant": str,
            "amount": float,
            "category": str,
        }
    """
    txns_raw = _request(f"/accounts/{account_id}/transactions?count={count}", access_token)

    transactions = []
    for txn in txns_raw:
        # Teller amounts are signed strings — negative means money out
        amount = abs(float(txn["amount"]))

        # Prefer counterparty name, fall back to description
        counterparty = txn.get("counterparty") or {}
        merchant = counterparty.get("name") or txn.get("description", "Unknown")

        details = txn.get("details") or {}
        category = details.get("category") or ""

        transactions.append({
            "date": txn["date"],
            "merchant": merchant,
            "amount": amount,
            "category": category,
        })

    return transactions
