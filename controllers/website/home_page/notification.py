import os
from fastapi import HTTPException, status
from firebase_admin import db
import json
from pywebpush import webpush, WebPushException
from backend.services.FirebaseServices import initialize_firebase
from dotenv import load_dotenv

initialize_firebase()

load_dotenv(dotenv_path='backend/.env')

VAPID_PUBLIC_KEY = os.getenv("VAPID_PUBLIC_KEY")
VAPID_PRIVATE_KEY = os.getenv("VAPID_PRIVATE_KEY")
ADMIN_EMAIL= os.getenv('VAPID_EMAIL')

class Notification:

    @staticmethod
    async def register(id: str, subscription):
        try:
           ref = db.reference(f'admin_notifications/{id}')
           ref.set({
                "endpoint": subscription.endpoint,
                "keys": subscription.keys
           })
           return {"status": "success", "message": "Subscription saved successfully."}

        except Exception as e: 
            raise HTTPException( status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error saving subscription: {str(e)}")
        


    @staticmethod
    async def unregister(id: str):
        try:
            ref = db.reference(f'admin_notifications/{id}')
            ref.delete()
            return {"status": "success", "message": "Subscription deleted successfully."}
        except Exception as e: 
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving subscription: {str(e)}"
            )
        
    @staticmethod
    async def checker(id: str):
        try:
            ref = db.reference(f'admin_notifications/{id}')
            existing = ref.get()

            if existing:
                return {"status": "success", "subscribed": True}
            else:
                 return {"status": "success", "subscribed": False}

        except Exception as e: 
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving subscription: {str(e)}"
            )
        


    @staticmethod
    async def send_notification(id: str, title: str, body: str):
        try:
            print(ADMIN_EMAIL)

            if not ADMIN_EMAIL:
                return

            ref = db.reference(f'admin_notifications/{id}')
            subscription = ref.get()

            if not subscription:
                raise HTTPException(status_code=404, detail="Subscription not found")

            payload = {
                "title": title,
                "body": body
            }

            webpush(
                subscription_info={
                    "endpoint": subscription['endpoint'],
                    "keys": {
                        "p256dh": subscription['keys']['p256dh'],
                        "auth": subscription['keys']['auth']
                    }
                },
                data=json.dumps(payload),
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={
                    "sub": f"mailto:{ADMIN_EMAIL}"
                }
            )

            return {"status": "success", "message": "Notification sent"}

        except WebPushException as ex:
            raise HTTPException(status_code=500, detail=f"Web push error: {str(ex)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"General error: {str(e)}")