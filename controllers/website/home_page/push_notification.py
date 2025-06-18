import json
from pywebpush import webpush, WebPushException
from backend.services.data_models import Subscription
from typing import List
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='backend/.env')


VAPID_PUBLIC_KEY =  os.getenv("VAPID_PUBLIC_KEY")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")



def add_subscription(subscription: Subscription):
    subscriptions.append(subscription)
    print(f"Added subscription: {subscription}")

def send_push_notification(title: str, body: str, icon: str, badge: str):
    if not subscriptions:
        raise Exception("No subscriptions found")

    payload = {
        "title": title,
        "body": body,
        "icon": icon,
        "badge": badge
    }

    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": sub.keys
                },
                data=json.dumps(payload),  
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={
                    "sub": "mailto:martdahao@gmail.com"  
                },
            )
            print(f"Notification sent to {sub.endpoint}")
        except WebPushException as e:
            print(f"Failed to send notification to {sub.endpoint}: {e}")

def unsubscribe(endpoint: str):
    global subscriptions
    subscriptions = [sub for sub in subscriptions if sub.endpoint != endpoint]
    print(f"Unsubscribed: {endpoint}")