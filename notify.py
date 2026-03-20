"""Send email digest via Gmail SMTP. Isolated so it's swappable later."""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import config


def send_email(html_body: str, subject: str | None = None) -> None:
    """Send an HTML email via Gmail SMTP.

    Args:
        html_body: The full HTML content of the email.
        subject: Optional override for the email subject line.
    """
    subject = subject or config.REPORT_TITLE

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = config.EMAIL_FROM
    msg["To"] = config.EMAIL_TO

    # Plain text fallback
    plain_text = "Your daily finance digest is ready. View the HTML version for full details."
    msg.attach(MIMEText(plain_text, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(config.GMAIL_SMTP_SERVER, config.GMAIL_SMTP_PORT) as server:
        server.starttls()
        server.login(config.EMAIL_FROM, config.GMAIL_APP_PASSWORD)
        server.sendmail(config.EMAIL_FROM, config.EMAIL_TO, msg.as_string())

    print(f"Email sent to {config.EMAIL_TO}")
