from fastapi import HTTPException, status,BackgroundTasks
from firebase_admin import auth,db,messaging
from fastapi.responses import JSONResponse
from backend.services.FirebaseServices import initialize_firebase
import requests
import traceback
import os
from datetime import datetime


initialize_firebase()



class PushNotificationFunctions:

    async def send_push_notification_all(self,message:str,title: str,background_tasks:BackgroundTasks):
     print('sending notification to user')
     try:
        recepients = await self.get_user_data()
        
        if not recepients:
            print('no recepient found registered')
            return
    
        for user_id, user_data in recepients.items():
            token = user_data.get('token')
            if token:
                background_tasks.add_task(self.send_fcm_notification, token, title, message)
        print('notification sent')
        return True
     except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))



    async def get_user_data(self):
        ref = db.reference(f'/notifications')
        data = ref.get()
        return data


    def notif_template(self,title,message,token):
        return {
            "to":token,
            "title":title,
                "body":message,
                    "data": {"info":"extra data"}
        }
    


    def send_fcm_notification(self, token: str, title: str, message: str):
       try:
            
            payload = {
                "to": token,
                "sound": "default",
                "title": title,
                "body": message,
                "data": {
                    "info": "extra data"
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



    async def add_push_notif(self,id: str, token: str):
        print('saving the notification')
        try:
            ref = db.reference(f'/notifications/{id}')
            to_save = {
                "token": token,
                "timestamp": datetime.utcnow().isoformat()
            }
            ref.set(to_save)
            print('Successfully saved the token to Firebase.')
            return {"message": "Token saved successfully"} 

        except Exception as e:
             traceback.print_exc()
             raise HTTPException(status_code=500, detail=str(e))
        

    async def remove_push_notif(self,id:str):
        print('dawdawdww')
        try:
            ref = db.reference(f'/notifications/{id}')
            ref.delete()
            return {"message": "notification removed successfully"} 
        except Exception as e:   
            raise HTTPException(status_code=500, detail=str(e))
        


    async def send_personal_notification(self,id:str,message:str,title: str,background_tasks:BackgroundTasks):
        try:
            ref = db.reference(f'/notifications/{id}')
            user_data = ref.get()
            if not user_data:
                print('no user found')
                return
            token = user_data.get('token')
            
            if token:
                background_tasks.add_task(self.send_fcm_notification, token, title, message)

            return True
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
