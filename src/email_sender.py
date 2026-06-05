import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.config import EMAIL_SENDER, EMAIL_APP_PASSWORD, EMAIL_RECEIVER


def send_email(subject: str, body: str) -> None:
    if not EMAIL_SENDER or not EMAIL_APP_PASSWORD or not EMAIL_RECEIVER:
        raise ValueError('Missing email config. Check .env file.')

    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL_SENDER, EMAIL_APP_PASSWORD)
        server.send_message(msg)

    print(f'[EMAIL SENT] {subject}')
