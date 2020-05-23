from flask_mail import Message
from app import mail

def send_email(subject , sender, recipients, text_body, html_body):
    message = Message(subject,sender=sender, recipients = recipients)
    message.body = text_body
    message.html = html_body
    mail.send(message)

def send_password_reset_email():
    print("not done yet")
