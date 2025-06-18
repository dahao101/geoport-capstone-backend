from fastapi import HTTPException, status, BackgroundTasks
from firebase_admin import auth,db
from firebase_admin.exceptions import FirebaseError 
from backend.services.email_sender import emailSender
from backend.services.FirebaseServices import initialize_firebase
from backend.services.email_templates.update_report_processing import update_report_processing
from backend.services.email_templates.update_report_solved import update_report_solved
from backend.controllers.application.homepage.send_push_notif import PushNotificationFunctions

initialize_firebase()

async def update_reports(report_id: str, report_status: str, passable_status: str,current_version:str, background_tasks: BackgroundTasks):
    try:
        print('updating report with :',report_id, report_status,passable_status, "with version ",current_version)
        ref = db.reference(f'reports/{report_id}')
        data = ref.get()
        reference_version = data.get('version')
        print('reference version is :', reference_version, "current version is :", current_version)
        if reference_version != current_version:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Your current version does not match with the current version in the database. Please refresh the page and try again."
            )

        update_data = {"status": report_status, "passable": passable_status,"version": int(current_version) + 1}
        ref.update(update_data)
         
        updated_report = ref.get()
        
        if not updated_report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report with ID {report_id} not found in the database."
            )
        
        user_id = updated_report.get('reference')
        user = auth.get_user(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="user not found in the registered accounts"
            )   
        

        email = user.email


        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not found in the updated report"
            )

        current_status = updated_report.get('status')  
        push_notifier = PushNotificationFunctions()
        name = updated_report['reporter']
        title = updated_report['TypeOfReport']
        id = updated_report['reference']

        if current_status == 'On going':
            template = update_report_processing(email, updated_report['reporter'], updated_report['location'])
            background_tasks.add_task(emailSender, email, "Report On going", template)
            message = f'Hi {name}, we want to inform you that the report you submitted is now marked as "On going".'
            await push_notifier.send_personal_notification(id, message, title, background_tasks)

        elif current_status == 'False Report':
            template = update_report_solved(email, updated_report['reporter'], updated_report['location'])
            background_tasks.add_task(emailSender, email, "Report flagged as False Report", template)
            message = f'Hi {name}, after review, the report you submitted has been marked as a "False Report". If you believe this is a mistake, feel free to contact us for clarification.'
            await push_notifier.send_personal_notification(id, message, title, background_tasks)

        elif current_status == 'Under Construction':
            template = update_report_solved(email, updated_report['reporter'], updated_report['location'])
            background_tasks.add_task(emailSender,email, "Report is Under Construction", template)
            message = f'Hi {name}, good news! The reported issue at your location is now under construction. Thank you for helping us improve the community.'
            await push_notifier.send_personal_notification(id, message, title, background_tasks)

        elif current_status in ['solved', 'Solved']:
            template = update_report_solved(email, updated_report['reporter'], updated_report['location'])
            background_tasks.add_task(emailSender, email, "Report Solved", template)
            message = f'Hi {name}, we’re happy to inform you that the issue you reported has been resolved. Thank you for your help in making the community better!'
            await push_notifier.send_personal_notification(id, message, title, background_tasks)

        return {"message": "Report updated successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred: {str(e)}"
        )
