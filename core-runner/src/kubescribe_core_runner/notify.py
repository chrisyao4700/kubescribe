from typing import Optional, List
import smtplib
from email.message import EmailMessage

def send_email(host: str, port: int, user: Optional[str], password: Optional[str], use_tls: bool,
               sender: str, recipients: List[str], subject: str, body: str) -> None:
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.set_content(body)

    if use_tls:
        with smtplib.SMTP(host, port) as s:
            s.starttls()
            if user and password:
                s.login(user, password)
            s.send_message(msg)
    else:
        with smtplib.SMTP(host, port) as s:
            if user and password:
                s.login(user, password)
            s.send_message(msg)
