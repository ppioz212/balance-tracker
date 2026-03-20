"""One-time setup: runs Teller Connect to enroll accounts and get an access token.

Run this locally:
    python setup_teller.py

It starts a small local server, opens Teller Connect in your browser,
captures the access token on success, and prints it to the terminal.
Save that token as the TELLER_ACCESS_TOKEN GitHub Actions secret.

Prerequisites:
    - A Teller application ID from https://teller.io/dashboard
    - Set TELLER_APPLICATION_ID environment variable
    - Optionally set TELLER_ENVIRONMENT (sandbox/development/production, defaults to sandbox)
"""

import http.server
import json
import os
import threading
import webbrowser


APPLICATION_ID = os.environ.get("TELLER_APPLICATION_ID", "")
ENVIRONMENT = os.environ.get("TELLER_ENVIRONMENT", "sandbox")
PORT = 8742


CONNECT_HTML = """<!DOCTYPE html>
<html>
<head><title>Teller Connect Setup</title></head>
<body style="font-family: sans-serif; max-width: 600px; margin: 40px auto; text-align: center;">
    <h1>Finance Tracker — Teller Setup</h1>
    <p>Click the button to connect your bank accounts and credit cards.</p>
    <button id="connect-btn" style="padding: 12px 24px; font-size: 16px; cursor: pointer;
        background: #0066ff; color: white; border: none; border-radius: 6px;">
        Connect with Teller
    </button>
    <p id="status" style="margin-top: 20px; color: #666;"></p>
    <script src="https://cdn.teller.io/connect/connect.js"></script>
    <script>
        var tellerConnect = TellerConnect.setup({
            applicationId: "%s",
            products: ["balance", "transactions"],
            environment: "%s",
            onSuccess: function(enrollment) {
                document.getElementById('status').textContent = 'Sending token to server...';
                fetch('/save-token', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        access_token: enrollment.accessToken,
                        enrollment_id: enrollment.enrollment.id,
                        institution: enrollment.enrollment.institution.name
                    })
                }).then(function(r) { return r.json(); }).then(function() {
                    document.getElementById('status').innerHTML =
                        '<strong style="color: green;">Done!</strong> Check your terminal for the access token. You can close this tab.';
                });
            },
            onExit: function() {
                document.getElementById('status').textContent = 'Connect was closed without completing enrollment.';
            },
            onFailure: function(failure) {
                document.getElementById('status').textContent = 'Error: ' + failure.message;
            }
        });
        document.getElementById('connect-btn').onclick = function() { tellerConnect.open(); };
    </script>
</body>
</html>"""


class SetupHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            html = CONNECT_HTML % (APPLICATION_ID, ENVIRONMENT)
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/save-token":
            length = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(length))

            print("\n" + "=" * 60)
            print("SUCCESS! Teller enrollment complete.")
            print(f"  Institution: {body.get('institution', 'N/A')}")
            print(f"  Enrollment ID: {body.get('enrollment_id', 'N/A')}")
            print(f"\n  Access Token: {body['access_token']}\n")
            print("Save this as the TELLER_ACCESS_TOKEN secret in GitHub Actions.")
            print("=" * 60 + "\n")

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())

            threading.Timer(1.0, lambda: os._exit(0)).start()
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def main():
    if not APPLICATION_ID:
        print("Error: Set TELLER_APPLICATION_ID environment variable first.")
        print("  export TELLER_APPLICATION_ID=app_xxxxx")
        print("\nGet your application ID from https://teller.io/dashboard")
        return

    print(f"Starting Teller Connect setup on http://localhost:{PORT}")
    print(f"Environment: {ENVIRONMENT}")
    print("Opening browser...")

    server = http.server.HTTPServer(("localhost", PORT), SetupHandler)
    webbrowser.open(f"http://localhost:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
