from fastapi.security import OAuth2PasswordBearer
import os
import time
import hmac
import hashlib
from backend.services.tokenGenerator import TokenGenerator
from backend.services.tokenChecker import TokenChecker
from typing import Optional, Union
from fastapi.responses import JSONResponse
from firebase_admin import auth, initialize_app, credentials
from backend.controllers.application.homepage.submit_report import submit_report
from fastapi import APIRouter,FastAPI,WebSocket, WebSocketDisconnect,Request,HTTPException,BackgroundTasks,File, UploadFile,Header,Query,Body,Form,Depends,status
from backend.services.data_models import *
from pydantic import BaseModel
from backend.controllers.website.home_page.fetch_all_reports import fetch_all_reports
import firebase_admin
from backend.controllers.application.homepage.validate_report import validate_image
from backend.services.FirebaseServices import initialize_firebase
from backend.controllers.website.home_page.fetch_user_data import fetch_user_data
from backend.controllers.application.homepage.fetch_user_report import FetchUserReported
from backend.controllers.application.homepage.userVerification import updateuserStatus
from backend.controllers.application.homepage.update_user_info import update_user_profile
from backend.controllers.website.home_page.change_password_pin_sender import send_pin_password
from backend.controllers.website.home_page.update_email_pin_sender  import send_pin_email
from backend.controllers.website.home_page.update_email_pin_verifier import update_email_verify_pin
from backend.controllers.website.home_page.change_password_pin_verifier import change_password_verify_pin
from backend.controllers.website.home_page.change_email import change_email
from backend.services.expired_key_checker import expired_key_remover
from backend.controllers.website.home_page.change_password import update_user_password
from backend.services.cloudinary_uploader import cloudinary_uploader
from backend.controllers.application.homepage.change_number import ChangeNumber
from backend.controllers.application.homepage.forgot_pasword import ForgotPasswordFunctions
from backend.controllers.application.homepage.send_push_notif import PushNotificationFunctions
from backend.controllers.website.home_page.reverse_location import reverse_location
from backend.controllers.application.homepage.routing_functions import *
from backend.controllers.application.homepage.submit_room_id import submit_id
from dotenv import load_dotenv
import shutil


load_dotenv(dotenv_path='backend/.env')
router = APIRouter()
active_connections = {}
initialize_firebase()
notification_functions = PushNotificationFunctions()




@router.post('/submit_reports')
async def submitReports(data: CreateReport,background_tasks: BackgroundTasks,authorization: str = Header(None)):
    print('trying to submit report')
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(content={'status': 'failed', 'message': 'Invalid or missing token'}, status_code=401)
   
    token = authorization.split(" ")[1]

    try:
        decoded_token = auth.verify_id_token(token)
        if not decoded_token:
            print('token not validated or invalid')
        print('Token validated')
        user_uid = decoded_token["uid"]
        user_email = decoded_token.get("email", "Unknown")
        print(f"Report submitted by {user_email} (UID: {user_uid})")

        response  =  await submit_report(data,background_tasks,user_email)

        if response:
            return JSONResponse(content={'status': 'success'})
        else:
            return JSONResponse(content={'status': 'failed'})
    except Exception as e:
        print(f"Error submitting report: {e}")   
        return JSONResponse(content={'status': 'failed', 'message': 'Unauthorized'}, status_code=401)

    



@router.post('/validate-report')
async def validate_report(image: UploadFile = File(...)):
    print("Received image:", image.filename) 
    try:
        response = await validate_image(image)
        return JSONResponse(content=response)
    except Exception as e:
        print(f"Error validating report: {e}")
        raise HTTPException(status_code=500, detail="Server error during validation.")
    

@router.websocket('/fetch-reports')
async def fetchReports(websocket: WebSocket):
    await websocket.accept()
    token = websocket.query_params.get('token')

    if not token:
        print("Token is missing")
        await websocket.send_json({"error": "Token missing"})
        await websocket.close()
        return

    try:
        # Verify token
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token["uid"]
    except Exception as e:
        print(f"Authentication failed: {e}")
        await websocket.send_json({"error": "Unauthorized"})
        await websocket.close()
        return

    active_connections[websocket.client] = websocket

    reports = await fetch_all_reports()
    await websocket.send_json(reports)

    while True:
        try:
            data = await websocket.receive_text()
            print(f"Received data: {data}")
            await websocket.send_json({"message": "Data received"})
        except WebSocketDisconnect:
            print("WebSocket disconnected")
            break



@router.get('/fetch-user-data')
async def fetchUserData(request: Request, id: str):
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Authorization header missing or invalid")
        
        token = auth_header.split("Bearer ")[1]

        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token["uid"]

        if user_id != id:
            raise HTTPException(status_code=403, detail="Invalid token for this user")
        
        print(f"User ID: {user_id} is authenticated")
        user_data = await fetch_user_data(id)
        return JSONResponse(content={"success": True, "data": user_data})

    except Exception as e:
        print(f"Error fetching user data: {e}")
        raise HTTPException(status_code=500, detail="Server error fetching user data.")


@router.get('/generate-signature')
async def generate_signature(public_id: str):
    cloud_name = os.getenv('CLOUD_NAME')
    api_key = os.getenv('CLOUDINARY_API_KEY')  # 🔥 Load from env instead of hardcoding
    secret_key = os.getenv('CLOUDINARY_SECRET_KEY')

    if not cloud_name or not api_key or not secret_key:
        raise HTTPException(status_code=500, detail="Cloudinary credentials missing")
    
    try:
        timestamp = str(int(time.time()))
        params_to_sign = f"public_id={public_id}&timestamp={timestamp}"

        signature = hmac.new(
            secret_key.encode("utf-8"),
            params_to_sign.encode("utf-8"),
            hashlib.sha1
        ).hexdigest()

        return {
            "cloud_name": cloud_name,
            "api_key": api_key,
            "timestamp": timestamp,
            "signature": signature,
            "upload_preset": "report_images"  # Make sure this matches your Cloudinary preset
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.get('/fetch-reported-reports')
async def FetchUSerReports(id: str = Query(...),authorization: str = Header(None)):
    print('fetching user reported data')

    token = authorization.split("Bearer ")[1]

    try:
        decoded_token = auth.verify_id_token(token)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    data = await FetchUserReported(id)  

    return JSONResponse(content={"success": True, "data": data},status_code=200)                                                


@router.patch('/update-status/{id}')
async def UpdateStatusAndProfile( id: str, user_data: UpdateUserRequest, authorization: str = Header(None)):
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")
    
    token = authorization.split("Bearer ")[1]
    decoded_token = auth.verify_id_token(token)


    if not decoded_token:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


    if decoded_token["uid"] != id:
        raise HTTPException(status_code=403, detail="Unauthorized user ID")

    update_data = await updateuserStatus(id, user_data.imageUrl)

    if not update_data:
        print('unsuccessful updating of data')
        raise HTTPException(status_code=500, detail="Failed to update user status")
    
    print('update successful')


    return {"message": "User status updated successfully!"}




@router.post('/create-account')
async def create_user_account(data:CreateUserAccount):
    return JSONResponse(content={"message": "User created successfully", "uid": data.uid})
    


@router.post('/change-name')
async def change_name(data:UpdateNameData, authorization: str = Header(None)):
    return JSONResponse(content={"message": "Name changed successfully", "uid": data.user_id})
    print('changing name')


@router.patch('/update-phone-number/{id}')
async def update_phone_number(id: str,data:ChangeNumberData, authorization: str = Header(None)):
        
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(content={'status': 'failed', 'message': 'Invalid or missing token'}, status_code=401)
            raise HTTPException(status_code=401, detail="Missing or invalid token")
    
        token = authorization.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token["uid"]

        if user_id != id:
            raise HTTPException(status_code=403, detail="Invalid token for this user")
        
        return JSONResponse(content={"message": "Phone number updated successfully", "uid": id})


@router.post('/update-user-info/{id}')
async def update_user_info(id: str, new_name: str = Form(...), new_image: Optional[UploadFile] = File(None),cloudinary_url: Optional[str] = Form(None),    authorization: str = Header(None)):

    print('updating user info')

    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(content={'status': 'failed', 'message': 'Invalid or missing token'}, status_code=401)

    token = authorization.split("Bearer ")[1]
    decoded_token = auth.verify_id_token(token)
    user_id = decoded_token["uid"]

    if user_id != id:
        raise HTTPException(status_code=403, detail="Invalid token for this user")

    if new_image:
        newImageUrl = await cloudinary_uploader(new_image, id)
        image_url = newImageUrl
        if not image_url:
            raise HTTPException(status_code=500, detail="Failed to upload image")
        print(f"Using uploaded image: {image_url}")
    elif cloudinary_url:
        image_url = cloudinary_url
        print(f"Using cloudinary image: {image_url}")
    else:
        raise HTTPException(status_code=400, detail="No image provided.")

    update_user = await update_user_profile(id, new_name, image_url)
    if not update_user:
        raise HTTPException(status_code=500, detail="Failed to update user profile")

    return JSONResponse(content={"message": "User profile updated successfully", "uid": id})



@router.post('/change_pass_send_pin')
async def change_pass_send_pin(data:app_change_password_send,background_tasks:BackgroundTasks):
    print('sending pin')
    try:

        isPinSent = await send_pin_password(data.email,background_tasks)
        if not isPinSent:
            raise HTTPException(status_code=500, detail="Failed to send pin")
        
    except Exception as e:
        return JSONResponse(content={'status': 'error', 'message': 'An unexpected error occurred.'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

 
@router.post('/change_pass_verify_pin')
async def change_pass_verify_pin(data:app_change_password_verify):
    try:
        await expired_key_remover()
        pin = data.pin
        email = data.email
        result = await change_password_verify_pin(pin,email)
        if not result:
            raise HTTPException(status_code=500, detail="Failed to send pin")
        return JSONResponse(content={"message": "Pin Verified Successfully"})
    except Exception as e:
        return JSONResponse(content={'status': 'error', 'message': 'An unexpected error occurred.'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


@router.post('/change-password')
async def change_password(data: change_password_data):
    print('change password reached')
    try:
        password = data.new_password
        email = data.email
        result = await update_user_password(email, password)
        
        return JSONResponse(content=result, status_code=200)

    except HTTPException as e:
        raise e  # Let FastAPI handle this properly
    except Exception as e:
        print(f"Unexpected error in route: {str(e)}")
        return JSONResponse(
            content={'status': 'error', 'message': 'An unexpected error occurred.'},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@router.post('/change-email-send-pin/{id}')
async def change_email_send_pin(id:str,background_tasks:BackgroundTasks, authorization: str = Header(None)):
    print('change email send pin')
    try:
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(content={'status': 'failed', 'message': 'Invalid or missing token'}, status_code=401)

        token = authorization.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token["uid"]

        if user_id != id:
            raise HTTPException(status_code=403, detail="Invalid token for this user")

        is_success = await send_pin_email(id,background_tasks)
        if not is_success:
            raise HTTPException(status_code=500, detail="Failed to send pin")
        
        return JSONResponse(content={'status': 'success'})  
    except Exception as e:
        return JSONResponse(content={"status":"error","message": "change email send pin error"},status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)    
    

@router.post('/change-email-verify-pin/{id}')
async def change_email_verify_pin(id: str, data: app_change_email_verify, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    try:
        token = authorization.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token["uid"]

        if user_id != id:
            raise HTTPException(status_code=403, detail="Invalid token for this user")
        
        is_verified = await update_email_verify_pin(id, data.inputted_pin)
        if not is_verified:
            raise HTTPException(status_code=403, detail="Incorrect verification PIN")

        return JSONResponse(content={'status': 'success'})
    
    except HTTPException as http_exc:
        raise http_exc  
    
    except Exception as e:
        print("Unhandled error:", e)
        return JSONResponse( content={"status": "error", "message": "change email verify pin error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@router.post('/change-email/{id}')
async def change_email_new(id:str,data:change_new_email,authorization: str = Header(None)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(content={'status': 'failed', 'message': 'Invalid or missing token'}, status_code=401)

        token = authorization.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token["uid"]

        if user_id != id:
            raise HTTPException(status_code=403, detail="Invalid token for this user")

        is_success = await change_email(id,data.new_email)
        if not is_success:
            raise HTTPException(status_code=500, detail="Failed to change email")
        
        return JSONResponse(content={'status': 'success'})  
    except Exception as e: 
        return JSONResponse(content={"status":"error","message": "change email error"},status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post('/change-phone-send-pin/{id}')   
async def change_number_sendpin(id:str,background_tasks:BackgroundTasks, authorization: str = Header(None)):
    print('change number send pin')
    try:
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(content={'status': 'failed', 'message': 'Invalid or missing token'}, status_code=401)

        token = authorization.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token["uid"]

        if user_id != id:
            raise HTTPException(status_code=403, detail="Invalid token for this user")
        
        change_number = ChangeNumber(number = '',user_id = id)
        send_pin = await change_number.send_verification_pin(background_tasks)
        if not send_pin:
            raise HTTPException(status_code=500, detail="Failed to send pin")
        return JSONResponse(content={'status': 'success'})
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(content={'status': 'error', 'message': 'An unexpected error occurred.'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

@router.post('/change-phone-verify-pin/{id}')
async def change_number_verify_pin(id:str,data:ChangeNumberData,authorization: str = Header(None)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(content={'status': 'failed', 'message': 'Invalid or missing token'}, status_code=401)
        
        token = authorization.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token["uid"]

        if user_id != id:
            raise HTTPException(status_code=403, detail="Invalid token for this user")
        
        change_number = ChangeNumber(number = data.inputted_pin,user_id = id)
        verify_pin = await change_number.verify_pin(data.inputted_pin)

        if not verify_pin:
            raise HTTPException(status_code=403, detail="Incorrect verification PIN")
        return JSONResponse(content={'status': 'success'})
    
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(content={'status': 'error', 'message': 'An unexpected error occurred.'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


@router.post('/change-phone/{id}')
async def change_number(id:str,data:NumberData,authorization: str = Header(None)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(content={'status': 'failed', 'message': 'Invalid or missing token'}, status_code=401)
        
        token = authorization.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token["uid"]

        if user_id != id:
            raise HTTPException(status_code=403, detail="Invalid token for this user")
        
        change = ChangeNumber()
        
        is_changed = await change.change_number(data.new_number,id)

        if not is_changed:
            raise HTTPException(status_code=500, detail="Failed to change number")
        return JSONResponse(content={'status': 'success'})

    except Exception as e:
        print("Error in change_number endpoint:", e) 
        return JSONResponse(content={'status': 'error', 'message': 'An unexpected error occurred.'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


@router.post('/apply-send-notif/{id}')
async def apply_push_notification(id:str,data:ApplyTokenData,authorization: str = Header(None)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(content={'status': 'failed', 'message': 'Invalid or missing token'}, status_code=401)
        
        token = authorization.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token["uid"]

        if user_id != id:
            raise HTTPException(status_code=403, detail="Invalid token for this user")
        expo_token = data.expoPushToken
        apply = await notification_functions.add_push_notif(id,expo_token)
        if not apply:
            return JSONResponse(content={'status': 'error', 'message': 'unable to save push notification.'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return JSONResponse(content={'status': 'success'})
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(content={'status': 'error', 'message': 'An unexpected error occurred.'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)




@router.post('/remove-send-notif/{id}')
async def apply_push_notification(id:str,authorization: str = Header(None)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(content={'status': 'failed', 'message': 'Invalid or missing token'}, status_code=401)
        
        token = authorization.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token["uid"]

        if user_id != id:
            raise HTTPException(status_code=403, detail="Invalid token for this user")
        apply = await notification_functions.remove_push_notif(id)
        if not apply:
            return JSONResponse(content={'status': 'error', 'message': 'unable to save push notification.'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        return JSONResponse(content={'status': 'success'})
    except Exception as e:
        print(f"Error: {e}")
        return JSONResponse(content={'status': 'error', 'message': 'An unexpected error occurred.'}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.post('/forgot-password-send-pin')
async def forgot_password_send_pin(data:forgotPasswordSendPin,background_tasks:BackgroundTasks):
    try:

        is_pin_send = await ForgotPasswordFunctions.change_password_send_pin(data.email,background_tasks)

        if not is_pin_send:
            raise HTTPException(status_code=500, detail="Something went wrong while sending the pin")
        
        return JSONResponse(content={'status': 'success'})
    except Exception as e:
        return JSONResponse(
            content={'status': 'error', 'message': e.detail},
            status_code=e.status_code
        )


@router.post('/forgot-password-verify-pin')
async def forgot_password_verify_pin(data:forgotPasswordVerifyPin):
    try:
        verify = await ForgotPasswordFunctions.change_password_verify_pin(data.pin,data.email)
        if not verify:
            raise HTTPException(status_code=403, detail="Invalid pin")
        
        return JSONResponse(content={'status': 'success'})
    except HTTPException as e:
        return JSONResponse(
            content={'status': 'error', 'message': e.detail},
            status_code=e.status_code
        )

@router.post('/reverse-location/{id}')
async def reverse_location_function(id:str,data:reverseLocationData,authorization: str = Header(None)):
    try:
        print('reverse location called with:', data)
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(content={'status': 'failed', 'message': 'Invalid or missing token'}, status_code=401)
        token = authorization.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token["uid"]

        if user_id != id:
            raise HTTPException(status_code=403, detail="Invalid token for this user")
        
        location_name = await reverse_location(data)
        print('location name:', location_name)
        return JSONResponse(content={"status": "success", "location": location_name}, status_code=200)

        
    except Exception as e:
        print("Unhandled error:", e)
        return JSONResponse( content={"status": "error", "message": "fetch reverse location error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@router.post('/request_route/{id}')
async def request_route(id:str, data: RouteFunctionData, authorization: str = Header(None)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(content={'status': 'failed', 'message': 'Invalid or missing token'}, status_code=401)
        
        token = authorization.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token["uid"]

        if user_id != id:
            raise HTTPException(status_code=403, detail="Invalid token for this user")
        route_data = await route_functions(data)
        if not route_data:
            raise HTTPException(status_code=500, detail="Failed to fetch routing data")
        
        return JSONResponse(content={"status": "success", "data": route_data}, status_code=200)
        
    except Exception as e:
        print("Unhandled error:", e)
        return JSONResponse( content={"status": "error", "message": "request route error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@router.post('/request_reroute/{id}')
async def request_route(id:str, data: RerouteFunctionData, authorization: str = Header(None)):
    try:
        if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(content={'status': 'failed', 'message': 'Invalid or missing token'}, status_code=401)
        
        token = authorization.split("Bearer ")[1]
        decoded_token = auth.verify_id_token(token)
        user_id = decoded_token["uid"]

        if user_id != id:
            raise HTTPException(status_code=403, detail="Invalid token for this user")
        route_data = await reroute_function(data)
        if not route_data:
            raise HTTPException(status_code=500, detail="Failed to fetch routing data")
        return JSONResponse(content={"status": "success", "data": route_data}, status_code=200)
        
    except Exception as e:
        print("Unhandled error:", e)
        return JSONResponse( content={"status": "error", "message": "request route error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.post('/generate-room-id/{id}')
async def submit_generated_room_id(id:str,data:GenerateRoomId,authorization: str = Header(None)):
    try:
          if not authorization or not authorization.startswith("Bearer "):
            return JSONResponse(content={'status': 'failed', 'message': 'Invalid or missing token'}, status_code=401)
        
          token = authorization.split("Bearer ")[1]
          decoded_token = auth.verify_id_token(token)
          user_id = decoded_token["uid"]

          if user_id != id:
              raise HTTPException(status_code=403, detail="Invalid token for this user")
          
          response_status = await submit_id(id,data.room_id)
          return JSONResponse(content=response_status, status_code=200)
    except Exception as e:
        print("Unhandled error:", e)
        return JSONResponse( content={"status": "error", "message": "request route error"}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

