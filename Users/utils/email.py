import smtplib
from email.message import EmailMessage
import os


def send_reset_email(to_email: str, reset_token: str):
    msg = EmailMessage()
    msg["Subject"] = "Password Reset Request"
    msg["From"] = os.getenv("SMTP_FROM_EMAIL")
    msg["To"] = to_email

    reset_link = f"http://localhost:3000/reset-password?token={reset_token}"

    msg.set_content(
        f"""
Hello,

You requested a password reset.

Click the link below to reset your password:
{reset_link}

This link will expire in 15 minutes.

If you did not request this, please ignore this email.
"""
    )

    with smtplib.SMTP(os.getenv("SMTP_HOST"), int(os.getenv("SMTP_PORT"))) as server:
        server.starttls()
        server.login(
            os.getenv("SMTP_USERNAME"),
            os.getenv("SMTP_PASSWORD")
        )
        server.send_message(msg)