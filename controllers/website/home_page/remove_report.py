from fastapi import HTTPException, status, BackgroundTasks
from firebase_admin import db, exceptions, auth
from backend.services.FirebaseServices import initialize_firebase
from backend.services.email_sender import emailSender
from backend.services.email_templates.report_deletion import delete_template
from concurrent.futures import ThreadPoolExecutor

initialize_firebase()

async def remove_report(report_id: str,currentVersion:str, background_tasks: BackgroundTasks):
    try:
        print(f"Attempting to remove report: {report_id}")
        
 
        ref = db.reference(f"reports/{report_id}")
        report = ref.get()
        old_version = report.get('version')

        if old_version != currentVersion:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Your current version does not match with the report version in the database")
        
        uid = report.get('reference') 
        
        authenticator_response = auth.get_user(uid)  
        email = authenticator_response.email
        
        if report is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
        
        print("Report retrieved successfully:", report)
        
        ref.delete()
        print("Report deleted successfully from the database.")
        
        print(email)
        
        template = delete_template(report['reporter'], report['location'])
        background_tasks.add_task(emailSender, email,"Report Deletion", template)
        
        return True
    
    except exceptions.FirebaseError as firebase_error:
        print("Firebase error in remove_report:", str(firebase_error))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Firebase error: {str(firebase_error)}"
        )
    
    except HTTPException as e:
        print("HTTPException:", str(e.detail))
        raise e
    
    except Exception as e:
        print("Error in remove_report:", str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
