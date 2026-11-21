"""E-mail versturen via SMTP. Zonder SMTP-instellingen wordt er niets verstuurd."""

import logging
import smtplib
import ssl
from email.message import EmailMessage

from .config import settings

log = logging.getLogger("ttt.mail")


def mail_enabled() -> bool:
    return bool(settings.smtp_host and settings.smtp_from)


def send_mail(to: str, subject: str, body: str) -> None:
    if not mail_enabled():
        return
    msg = EmailMessage()
    msg["From"] = settings.smtp_from
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)
    try:
        context = ssl.create_default_context()
        if settings.smtp_security == "ssl":
            server = smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, context=context, timeout=20)
        else:
            server = smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20)
            if settings.smtp_security == "starttls":
                server.starttls(context=context)
        with server:
            if settings.smtp_user:
                server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
    except (OSError, smtplib.SMTPException):
        # Een mislukte mail mag het opslaan van notulen niet tegenhouden.
        log.exception("Mail kon niet worden verstuurd")
