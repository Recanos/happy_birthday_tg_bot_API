import time
from celery import Celery
import smtplib
from email.message import EmailMessage

from config import SMTP_USER, SMTP_PASS

celery = Celery('tasks', broker='redis://localhost:6379')

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


def create_email_msg(data):
    email = EmailMessage()
    email["Subject"] = "Happy Birthday!"
    email["From"] = SMTP_USER
    email["To"] = SMTP_USER
    email.set_content(", ".join([user['name'] for user in data]))
    return email


@celery.task
def send_email(data):
    email = create_email_msg(data)

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(email)
