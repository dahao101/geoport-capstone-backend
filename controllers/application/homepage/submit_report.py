from fastapi import HTTPException, status,Header, BackgroundTasks
from firebase_admin import auth,db

from backend.services.FirebaseServices import initialize_firebase
from backend.services.email_sender import emailSender
from backend.services.email_templates.report_notification_sender import update_report_processing
from backend.services.tokenChecker import TokenChecker
from concurrent.futures import ThreadPoolExecutor
from backend.services.location_validator import generate_report
from backend.controllers.website.home_page.notification import Notification
from backend.controllers.application.homepage.send_push_notif import PushNotificationFunctions
from PIL import Image
import io
from ultralytics import YOLO


initialize_firebase()
executor = ThreadPoolExecutor(1)
token_checker = TokenChecker()

severity_model = YOLO("backend/services/models/severity_model/best.pt")

async def submit_report(data, background_tasks: BackgroundTasks, user_email: str):
    try:
        print("Running the submit report function", flush=True)

        severity_results = []
        if data.TypeOfReport == 'vehicle collision':
           severity_results = severity_model.predict(data.image)
           class_names = severity_model.names 

           
           if severity_results:
               for r in severity_results:
                   for box in r.boxes:
                       cls_id = int(box.cls[0])
                       conf = float(box.conf[0])
                       severity = class_names[cls_id]
                       if severity == 'fire':
                           severity = 'normal'
                       print(f"Severity: {severity}, Confidence: {conf}")
           else:
               severity = 'normal'
               print("No severity results detected.")
        
        print('the severity results: ========================= ', severity_results)

        latitude = data.location.get("latitude", "Unknown")
        longitude = data.location.get("longitude", "Unknown")
        
        # isValid = generate_report(latitude,longitude)

        # if not isValid["status"]:
        #     print('not valid location')
        #     raise HTTPException(status_code=400, detail="Invalid location. Report not submitted.")
        
        ref = db.reference('/reports').push()
        report_data = {
            "DateAndTime": data.DateAndTime,
            "Severity": "normal",
            "TypeOfReport": data.TypeOfReport, 
            "image": data.image,
            "location": {
                "latitude": latitude,
                "longitude": longitude
            },
            "passable": data.passable,
            "reference": data.reference,
            "reporter": data.reporter,
            "status": data.status
        }

        ref.set(report_data)

        template = update_report_processing( data.reporter, data.TypeOfReport,'Geoport-malaybalay Response Team')
        background_tasks.add_task( lambda: executor.submit(emailSender, user_email, "Report Submission Confirmation", template))
        name = data.reporter
        message = f'Hello {name}, someone just shared a new report in your community! check it out!'
        title = 'Nearby Alerts'
        push_notifier = PushNotificationFunctions()
        await push_notifier.send_push_notification_all(message, title, background_tasks)
        # await send_push_notification(message,title)


        return True
    
    except Exception as e:
        print(f"Error storing report: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


async def send_push_notification(message: str, title: str):
        try:
            ref = db.reference('admin_notifications') 
            subscriptions = ref.get()  

            if not subscriptions:
                print("No subscriptions found.")
                return

            for admin_id, subscription in subscriptions.items():
                await Notification.send_notification(
                    id=admin_id,
                    title=title,
                    body=message
                )

            print("Notifications sent to all admins.")
        
        except Exception as e:
            print(f"Error sending notifications: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error sending notifications: {str(e)}")