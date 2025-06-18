from fastapi import HTTPException, status, BackgroundTasks
from firebase_admin import auth, db
from fastapi.responses import JSONResponse
from backend.services.FirebaseServices import initialize_firebase
import requests
import traceback
from datetime import datetime

initialize_firebase()

async def send_user_signal_call(user_id: str, room_token: str, type: str, background_tasks: BackgroundTasks):
    try:
        ref = db.reference(f'/notifications/{user_id}')
        user_data = ref.get()

        if not user_data:
            print('No user found')
            return JSONResponse(status_code=404, content={"detail": "User not found"})

        token = user_data.get('token')

        if token:
            background_tasks.add_task(send_fcm_notification, token, type, room_token)

        return {"success": True, "message": "User status updated successfully!"}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


def send_fcm_notification(token: str, title: str, message: str):
    try:
        payload = {
            "to": token,
            "sound": "default",
            "title": "Incomming Call from Admin",
            "body": "Tap to answer the call",
            "data":{
                "type":title,
                "room_token":message
            }
            
        }
        print(payload)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.post("https://exp.host/--/api/v2/push/send", json=payload, headers=headers)

        if response.status_code == 200:
            print(f"Notification sent to {token}")
        else:
            print(f"Failed to send notification: {response.status_code}, {response.text}")

    except Exception as e:
        print(f"Error sending Expo push notification: {e}")
