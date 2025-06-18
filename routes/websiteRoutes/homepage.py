from fastapi.responses import JSONResponse
# from fastapi import APIRouter,FastAPI,WebSocket,Query, WebSocketDisconnect,HTTPException,Body,BackgroundTasks,status,File,Form,Header, UploadFile, HTTPException
from fastapi import *
from backend.controllers.website.login_page.login import loginhandler
from backend.controllers.website.login_page.forgotPassword import forgotPasswordHandler
from backend.controllers.website.login_page.signup import createAccountHandler
from backend.controllers.website.home_page.fetch_user_data import fetch_user_data
from backend.controllers.website.home_page.fetch_all_reports import fetch_all_reports
from backend.controllers.website.home_page.analytics_data import get_analytics_data
from backend.controllers.website.home_page.update_reports import update_reports
from backend.controllers.website.home_page.remove_report import remove_report
from backend.controllers.website.home_page.change_email import change_email
from backend.services.cloudinary_uploader import cloudinary_uploader
from backend.controllers.website.home_page.change_password_pin_verifier import change_password_verify_pin
from backend.controllers.website.home_page.update_email_pin_sender import send_pin_email
from backend.controllers.website.home_page.update_email_pin_verifier import update_email_verify_pin
from backend.controllers.website.home_page.update_name import update_name
from backend.controllers.website.home_page.fetch_logs import fetch_logs
from backend.services.data_models import *
from backend.controllers.website.home_page.push_notification import send_push_notification,add_subscription,unsubscribe
from backend.services.expired_key_checker import expired_key_remover
from backend.controllers.website.home_page.change_password_pin_sender import send_pin_password
from backend.controllers.website.home_page.notification import Notification
from backend.controllers.website.home_page.responder_functions import *
from backend.controllers.website.home_page.analytic_functions import *
from backend.controllers.website.home_page.fetch_room_id import feth_users_room_id
from backend.controllers.website.home_page.livekit_token_generator import token_generator
from backend.controllers.application.homepage.send_signal_call import send_user_signal_call
import asyncio
from firebase_admin import auth
from pydantic import BaseModel

 
router = APIRouter()
active_connections = {}


 

@router.get('/fetch_user_data/{id}')
async def fetch_details(id: str, authorization: str = Header(None)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]
        
        try:
            decoded_token = auth.verify_id_token(token)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")
        
        user_data = await fetch_user_data(id)
        
        return JSONResponse(content=user_data)

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal Server Error")
        



@router.patch('/update_report/{id}')
async def update_report(id:str,background_task:BackgroundTasks,report: dict = Body(...), authorization: str = Header(None)):

    try:

        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]
        
        try:
            decoded_token = auth.verify_id_token(token)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")

        report_id = report.get("report_id")
        status = report.get("status")
        passable_status = report.get('value')
        current_version = report.get('currentVersion')
        print('backend reach during updating report data',report_id,status,current_version)
        if not report_id or not status:
            raise HTTPException(status_code=400, detail="Missing report_id or status")
        report  = await update_reports(report_id,status,passable_status,current_version,background_task)
        if(report):
            return JSONResponse(content={'status':'success'})
        else:
            return JSONResponse(content={'status':'failed'})
            
    except HTTPException as e:
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=e.status_code)





@router.post('/remove_reports/{id}')
async def remove_report_data(id:str,data: RemoveReport,background_tasks: BackgroundTasks, authorization: str = Header(None)):
    print('Successfully reached the remove report function')
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]
        
        try:
            decoded_token = auth.verify_id_token(token)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")
        
        result = await remove_report(data.report_id,data.currentVersion,background_tasks)
        if result:
            return JSONResponse(content={'status': 'success'})
        else:
            return JSONResponse(content={'status': 'failed'})
    except HTTPException as e:
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=e.status_code)



@router.patch('/update_password')
async def update_password(data:UpdatePassword):
    print('update password reach')
    try:
        print('running the update password')
    except HTTPException as e:
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=e.status_code)


@router.post('/create_report')
async def create_report(data:CreateReport, authorization: str = Header(None)):
    print('create report reached')
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        token = authorization.split("Bearer ")[1]
        try:
            decoded_token = auth.verify_id_token(token)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")
        

        print('running the create report')
    except HTTPException as e:
        return JSONResponse(content={'status': 'error', 'message': str(e)}, status_code=e.status_code)


@router.post("/subscribe")
async def subscribe_to_push(subscription: Subscription):
    print('subscription reached')
    try:
        add_subscription(subscription)
        return {"message": "Subscription added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
@router.post("/send-notification")
async def send_notification(title: str, body: str):
    try:
        icon = "images/icon.png"  
        badge = "images/badge.png"
        send_push_notification(title, body, icon, badge)
        return {"message": "Notification sent to all subscribers"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post('/unsubscribe')
async def unsubscribe_from_push(subscription: Subscription):
    print('Unsubscribe request received')
    try:
        unsubscribe(subscription.endpoint)  
        return {"message": "Unsubscribed successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.post('/update_email_send_pin/{id}')
async def send_verification_key(id:str, background_tasks: BackgroundTasks, authorization: str = Header(None)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        token = authorization.split("Bearer ")[1]
        try:
            decoded_token = auth.verify_id_token(token)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")
        
        result = await send_pin_email(id, background_tasks) 
        if not result:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error occurred")
        
        return JSONResponse(content={'status': 'success'})  
    
    except HTTPException as e:
        return JSONResponse(content={'status': 'error', 'message': str(e.detail)}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={'status': 'error', 'message': 'An unexpected error occurred.'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



@router.post('/update_email_verify_pin/{id}')
async def verify_pin(id:str,data: UpdateEmailVerifypin, authorization: str = Header(None)):

    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]
        
        try:
            decoded_token = auth.verify_id_token(token)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")
        
        await expired_key_remover()

        result = await update_email_verify_pin(id, data.inputted_pin)
        
        if not result:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unexpected error occurred")

        return JSONResponse(content={'status': 'success', 'message': 'PIN verification successful.'}, status_code=200)
    
    except HTTPException as e:
        return JSONResponse(content={'status': 'error', 'message': str(e.detail)}, status_code=e.status_code)
    
    except Exception as e:
        return JSONResponse(content={'status': 'error', 'message': 'An unexpected error occurred.'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post('/change_email')
async def update_email(data: UpdateEmail, authorization: str = Header(None)):
    print('Running the change email function')
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]
        
        try:
            decoded_token = auth.verify_id_token(token)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != data.user_id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")


        response = await change_email(data.user_id, data.new_email)

        return JSONResponse(content={'status': 'success', 'message': response['message']}, status_code=200)

    except HTTPException as e:
        return JSONResponse(content={'status': 'error', 'message': str(e.detail)}, status_code=e.status_code)

    except Exception as e:
        print(f"Unexpected error: {str(e)}")  
        return JSONResponse(content={'status': 'error', 'message': 'An unexpected error occurred.'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)




@router.post('/update_profile')
async def update_name_function( user_id: str = Form(...), new_name: str = Form(...),image: UploadFile = File(None),image_link: str = Form(None),authorization: str = Header(None)):
    try:

        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]
        
        try:
            decoded_token = auth.verify_id_token(token)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")

        await expired_key_remover()
        image_url = None
        
        if image:
            upload_result = await cloudinary_uploader(image,user_id)
            print(f"Upload result: {upload_result}") 

            if isinstance(upload_result, dict):
                print(f"Upload result is a dictionary: {upload_result}")
                if 'secure_url' in upload_result:
                    image_url = upload_result['secure_url']
                    print(f"Image URL: {image_url}")
                else:
                    print("Error: 'secure_url' not found in the upload result.")
                    raise HTTPException(status_code=400, detail="Failed to get secure_url from upload result.")

            elif isinstance(upload_result, str):
                image_url = upload_result
                print(f"Received image URL: {image_url}")
            else:
                print(f"Error: upload_result is neither a dictionary nor a string: {upload_result}")
                raise HTTPException(status_code=400, detail="Unexpected upload result format.")


        if image_link and not image:
            image_url = image_link

        if not image_url and not image_link:
            raise HTTPException(status_code=400, detail="No image or image link provided.")
        print(f"Updating profile for user {user_id} with new name: {new_name} and image URL: {image_url}")
        update_result = await update_name(user_id, new_name, image_url)
        
        if not update_result:
            return JSONResponse(content={'status': 'failed', 'message': 'Failed to update profile.'}, status_code=400)

        return JSONResponse(content={'status': 'success', 'message': 'Profile updated successfully.'}, status_code=200)
    
    except HTTPException as e:
        return JSONResponse(content={'status': 'error', 'message': str(e.detail)}, status_code=e.status_code)
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return JSONResponse(content={'status': 'error', 'message': 'An unexpected error occurred.'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



@router.get('/fetch_logs')
async def get_logs():
    logs = await fetch_logs()  
    return JSONResponse(content=logs)


@router.post('/send_pin/{id}')
async def sending_pin(id: str, background_tasks: BackgroundTasks, authorization: str = Header(None)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]
        
        try:
            decoded_token = auth.verify_id_token(token)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")
        
        user_id = id.strip()
        print('user_id', user_id)
        if not user_id:
            print('no id')
            return JSONResponse(content={"message": "User ID is required"}, status_code=400)

        response = await send_pin_password(id, background_tasks)

        if response is True:
            return JSONResponse(content={"message": "PIN sent successfully"}, status_code=200)
        else:
            return JSONResponse(content={"message": str(response)}, status_code=400)
        
    except HTTPException as e:
        return JSONResponse(content={'status': 'error', 'message': e.detail}, status_code=e.status_code)
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        return JSONResponse(content={'status': 'error', 'message': 'An unexpected error occurred.'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)



@router.post('/verify_pin')
async def verifying_pin(user_data:VerifyPin, authorization: str = Header(None)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]
        
        try:
            decoded_token = auth.verify_id_token(token)
        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != user_data.user_id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")
        
        inputted_pin = user_data.inputted_pin
        user_id = user_data.user_id
        response = await change_password_verify_pin(inputted_pin,user_id)
        
        if response is True:
            return JSONResponse(content={"message": "Pin is verified"}, status_code=200)
        else:
            return JSONResponse(content={"message": str(response)}, status_code=400)
    except HTTPException as e:
        return JSONResponse(content={'status': 'error', 'message': 'An unexpected error occurred.'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

  


#=========================== WEB SOCKET ROUTES =================================================
@router.websocket("/fetch_reported_data")
async def fetch_data(websocket: WebSocket):
    await websocket.accept()
    active_connections[websocket] = True
    try:
        reports = await fetch_all_reports()
        await websocket.send_json(reports) 

        while True:
            await asyncio.sleep(10) 
            reports = await fetch_all_reports()  
            await websocket.send_json(reports)

    except WebSocketDisconnect:
        print("WebSocket disconnected")
        del active_connections[websocket]
    except Exception as e:
        print(f"Error: {e}")
        await websocket.send_json({"error": "Something went wrong"})
        del active_connections[websocket]



@router.get('/fetch_reports')
async def fetch_alL_reports(authorization: str = Header(None)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]
        try:
            decoded_token = auth.verify_id_token(token)

        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")
        
        reports = await fetch_all_reports()

        if not reports:
            return JSONResponse(content={"message": str(reports)}, status_code=400)
        
        return JSONResponse(content=reports)
    
    except HTTPException as e: 
        return JSONResponse(content={'status': 'error', 'message': 'An unexpected error occurred.'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@router.post('/register/{id}')
async def register_admin_notification(id:str,subscription: RegisterPushNotification,authorization: str = Header(None)):
    try:
        print(f"Received subscription: {subscription}")
    
        print(f"Endpoint: {subscription.endpoint}")
        print(f"Keys: {subscription.keys}")

        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]

        try:    
            decoded_token = auth.verify_id_token(token)

        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")
        
        registration_result = await Notification.register(id, subscription)
        
        # Return the result of the registration
        return JSONResponse(content=registration_result, status_code=status.HTTP_200_OK)
    except HTTPException as e:
        return JSONResponse(content={'status': 'error', 'message': 'An unexpected error occurred.'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@router.post('/unregister/{id}')
async def unregister_admin_notification(id:str,authorization: str = Header(None)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]

        try:
            decoded_token = auth.verify_id_token(token)

        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")


        remove_registration_result = await Notification.unregister(id)
    except HTTPException as e:
        return JSONResponse(content={'status': 'error', 'message': 'An unexpected error occurred.'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@router.post('/subscription-checker/{id}')
async def registration_checker(id:str,authorization: str = Header(None)):
    try:    
        if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]

        try:
            decoded_token = auth.verify_id_token(token)

        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")

        registration_checker_result = await Notification.checker(id)
        
        if registration_checker_result:
            return registration_checker_result
        else:
            raise HTTPException(status_code=500, detail="Failed to check subscription status")
        
    except HTTPException as e:
        return JSONResponse(content={'status': 'error', 'message': 'An unexpected error occurred.'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@router.post('/disable-responder-account/{id}')
async def disable_responder_account(id: str, data: DisableResponder, authorization: str = Header(None)):
    try:
        print(data)
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]

        try:
            decoded_token = auth.verify_id_token(token)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")
        
        result = await disable_responder(data)
        
        return JSONResponse(content={"status": result["status"]}, status_code=200)

    except HTTPException as e:
        return JSONResponse(content={"status": "error", "message": e.detail}, status_code=e.status_code)

    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": "An unexpected error occurred."},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.post('/remove-responder-account/{id}')
async def remove_responder_account(id:str,data:RemoveResponder,authorization: str = Header(None)):
        if not authorization or not authorization.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]

        try:
            decoded_token = auth.verify_id_token(token)

        except Exception as e:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")
        
        result = await remove_responder(data.user_id)

        return JSONResponse(content={"status": result["status"]}, status_code=200)
    
@router.post('/create-responder-account/{id}')
async def create_responder(id: str, data: CreateResponder, authorization: str = Header(None)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]

        try:
            decoded_token = auth.verify_id_token(token)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")
        
        result = await create_responder_account(data)
     
        return JSONResponse(
            content={
                "status": result["status"],
                "message": result["message"],
                "uid": result["uid"]
            },
            status_code=200
        )

    except HTTPException as e:
        return JSONResponse(content={ "status": "error","message": e.detail},status_code=e.status_code)

    except Exception as e:
        return JSONResponse( content={"status": "error", "message": f"Unexpected error: {str(e)}"},status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)   
    
@router.get('/fetch-responder-account/{id}')
async def fetch_responder(id: str, authorization: str = Header(None)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]

        try:
            decoded_token = auth.verify_id_token(token)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")
        
        result =  await fetch_responder_data()
        return JSONResponse(
            content={
                "status": result["status"],
                "data": result["data"]
            },
            status_code=200
        )

    except HTTPException as e:
        return JSONResponse(content={ "status": "error","message": e.detail},status_code=e.status_code)

    except Exception as e:
        return JSONResponse( content={"status": "error", "message": f"Unexpected error: {str(e)}"},status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)   
    
@router.post('/update-responder-account/{id}')
async def update_responder_account(id: str, data: UpdateResponder, authorization: str = Header(None)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")

        token = authorization.split("Bearer ")[1]

        try:
            decoded_token = auth.verify_id_token(token)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")

        result = await update_responder(data)

        return JSONResponse(
            content={
                "status": result["status"],
                "data": result["auth_uid"]
            },
            status_code=200
        )

    except HTTPException as e:
        raise e  
    except Exception as e:
        return JSONResponse(
            content={'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get('/fetch-analytics-data/{id}')
async def fetch_analytics_data(id:str,authorization: str = Header(None)):
    try:
        print('reacjhed')
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]
        print(token)
        try:
            decoded_token = auth.verify_id_token(token)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")
        
        analytics_data = await get_analytics_data()

        if not analytics_data:
            return JSONResponse(content={"message": str(analytics_data)}, status_code=400)
        
        return JSONResponse(content=analytics_data)
    except HTTPException as e:
        return JSONResponse(content={ "status": "error","message": e.detail},status_code=e.status_code)

    except Exception as e:
        print('dkajwndauiwdbkuldbawuyb')
        return JSONResponse( content={"status": "error", "message": f"Unexpected error: {str(e)}"},status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)   
    

@router.get('/fetch-geocoded-coordinates/{id}')
async def geocode_address_data(id:str,authorization: str = Header(None)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]

        try:
            decoded_token = auth.verify_id_token(token)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")
        
        data = await rank_each_highest_barangay()
        if not data:
            return JSONResponse(content={"message": str(data)}, status_code=400)
        return JSONResponse(content=data, status_code=200)
    except Exception as e:
        print('dkajwndauiwdbkuldbawuyb')
        return JSONResponse( content={"status": "error", "message": f"Unexpected error: {str(e)}"},status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)   
    

@router.post('/fetch_room_id/{id}')
async def fetch_user_room_id(id:str,data:GetRoomId,authorization: str = Header(None)):
    try:
        print('REACHED ',data)
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]

        try:
            decoded_token = auth.verify_id_token(token)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")
        
        result_data = await feth_users_room_id(data.user_id)
        print(result_data)
        return JSONResponse(content=result_data, status_code=200)
    except HTTPException as http_err:
        raise http_err
    except Exception as e:
        print('dkajwndauiwdbkuldbawuyb')
        return JSONResponse( content={"status": "error", "message": f"Unexpected error: {str(e)}"},status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)   
    
@router.post('/generate-livekit-token/{id}')
async def generate_livekit_token(id:str,data:LivekitTokenGenerator,authorization: str = Header(None)):
     try:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]

        try:
            decoded_token = auth.verify_id_token(token)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")
        
        user_id = data.user_id
        call_type = data.type
        generated_token = await token_generator(user_id,call_type)
        
        return JSONResponse(content=generated_token, status_code=200)
     except Exception as e:
         return JSONResponse( content={"status": "error", "message": f"Unexpected error: {str(e)}"},status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)   
    
    
@router.post('/send-call-notification/{id}')
async def  send_call_notification(id:str,data:SendCallSignal,background_task:BackgroundTasks,authorization: str = Header(None)):
    try:
        print('reached sending push notif')
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid token")
        
        token = authorization.split("Bearer ")[1]

        try:
            decoded_token = auth.verify_id_token(token)
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        if decoded_token["uid"] != id:
            raise HTTPException(status_code=403, detail="Unauthorized user ID")
        
        user_id = data.user_id
        type = data.type
        room_token = data.room_token
        result = await send_user_signal_call(user_id,room_token,type,background_task)
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
         return JSONResponse( content={"status": "error", "message": f"Unexpected error: {str(e)}"},status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)   
    
# tokenGenerator = TokenGenerator()
# tokenChecker = TokenChecker()
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")