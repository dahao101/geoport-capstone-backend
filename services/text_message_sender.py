import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path='../.env')

sender_email = os.getenv("EMAIL_SENDER")
app_key = os.getenv("APP_PASSWORD")


def send_sms_via_email(phone_number, subject, message_body, carrier_gateways):
    for carrier_gateway in carrier_gateways:
        try:
            if not sender_email or not app_key:
                raise ValueError("Email sender or password not properly loaded.")

            sms_gateway = f"{phone_number}@{carrier_gateway}"
            print(f"Sending SMS to {sms_gateway}")
            message = MIMEMultipart()
            message["From"] = sender_email
            message["To"] = sms_gateway
            message["Subject"] = subject
            
            message.attach(MIMEText(message_body, "plain"))

            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(sender_email, app_key)  
                server.sendmail(sender_email, sms_gateway, message.as_string())
                print(f"SMS sent to {phone_number} via {carrier_gateway}")
                return 

        except Exception as e:
            print(f"Failed to send SMS via {carrier_gateway}: {str(e)}")
            continue    
    
    print(f"Failed to send SMS to {phone_number} after trying all providers.")
    raise Exception(f"Could not send SMS to {phone_number}.")


phone_number = "6399922174494"  
subject = "Test SMS"
message_body = "Hello, this is a test message."

carrier_gateways = ["tmnet.ph", "smart.com.ph", "tnt.com.ph"]

send_sms_via_email(phone_number, subject, message_body, carrier_gateways)
