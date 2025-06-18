import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='backend/.env')
sender_email = os.getenv("EMAIL_SENDER")
password = os.getenv("APP_PASSWORD")

def emailSender(email, subject, template):
    print('email receiver is ',email)
    print('email sender is running')
    try:
        if not sender_email or not password:
            raise ValueError("Email sender or password not properly loaded.")
        receiver_email = email
        print('receiver email is ',receiver_email)
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = receiver_email
        message["Subject"] = subject
        message.attach(MIMEText(template, "html"))
        
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print(f"Email sent to {receiver_email}")

    except Exception as e:
        print(f"Failed to send email: {str(e)}")
        raise e
