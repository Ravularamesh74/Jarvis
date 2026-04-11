import smtplib
import imaplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import asyncio
import os

from utils.logger import get_logger

logger = get_logger("EmailIntegration")


class EmailClient:
    """
    📧 Email Integration

    Supports:
    - Sending emails
    - Reading inbox
    """

    def __init__(self):
        self.email_user = os.getenv("EMAIL_USER")
        self.email_password = os.getenv("EMAIL_PASSWORD")

        # Default Gmail config
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

        self.imap_server = "imap.gmail.com"

    # =============================
    # 📤 SEND EMAIL
    # =============================
    def send_email(self, to: str, subject: str, body: str) -> str:
        try:
            msg = MIMEMultipart()
            msg["From"] = self.email_user
            msg["To"] = to
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_user, self.email_password)

            server.send_message(msg)
            server.quit()

            logger.info(f"Email sent to {to}")
            return "Email sent successfully."

        except Exception as e:
            logger.error(f"Email send failed: {e}")
            return "Failed to send email."

    # =============================
    # 📥 READ EMAILS
    # =============================
    def read_emails(self, limit: int = 5):
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email_user, self.email_password)
            mail.select("inbox")

            status, messages = mail.search(None, "ALL")

            email_ids = messages[0].split()[-limit:]

            emails = []

            for eid in reversed(email_ids):
                _, msg_data = mail.fetch(eid, "(RFC822)")

                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])

                        subject = msg["subject"]
                        sender = msg["from"]

                        body = self._get_body(msg)

                        emails.append({
                            "from": sender,
                            "subject": subject,
                            "body": body[:500]
                        })

            mail.logout()
            return emails

        except Exception as e:
            logger.error(f"Read email failed: {e}")
            return []

    # =============================
    # 📄 EXTRACT BODY
    # =============================
    def _get_body(self, msg):
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    return part.get_payload(decode=True).decode(errors="ignore")
        else:
            return msg.get_payload(decode=True).decode(errors="ignore")

        return ""

    # =============================
    # ⚡ ASYNC WRAPPERS
    # =============================
    async def send_async(self, to: str, subject: str, body: str):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: self.send_email(to, subject, body)
        )

    async def read_async(self, limit: int = 5):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, lambda: self.read_emails(limit)
        )