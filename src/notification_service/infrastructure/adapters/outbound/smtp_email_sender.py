# src/notification_service/infrastructure/adapters/outbound/smtp_email_sender.py
import smtplib
from email.message import EmailMessage

from ....domain.service.notification_service import IEmailSender


class SMTPEmailSender(IEmailSender):
    def __init__(
        self,
        smtp_host: str,
        smtp_port: int,
        smtp_user: str,
        smtp_password: str,
    ) -> None:
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port
        self._smtp_user = smtp_user
        self._smtp_password = smtp_password

    def send(self, to_email: str, subject: str, body: str) -> None:
        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = self._smtp_user
        message["To"] = to_email
        message.set_content(body)

        with smtplib.SMTP(self._smtp_host, self._smtp_port) as smtp:
            smtp.starttls()
            smtp.login(self._smtp_user, self._smtp_password)
            smtp.send_message(message)
