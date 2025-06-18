from fastapi import HTTPException, status,BackgroundTasks
from firebase_admin import db, auth
from datetime import datetime
import traceback
from backend.services.email_templates.pin_verification import pin_sender_template
from backend.services.pin_generator import create_pin
from backend.services.email_sender import emailSender
from fastapi import HTTPException, status, BackgroundTasks
from firebase_admin import db, auth
from backend.services.FirebaseServices import initialize_firebase


initialize_firebase()
class ForgotPasswordFunctions:
    @staticmethod
    async def change_password_send_pin(email: str,background_tasks:BackgroundTasks):
        try:
            
            user = auth.get_user_by_email(email)
            if not user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not registered")

            user_id = user.uid
            email = user.email 
            ref = db.reference(f'users/{user_id}')
            user_data = ref.get()
            name = user_data['name']
    
            await check_db(user_id)

            pin, expiration_time = create_pin()
            expiration_time_str = expiration_time.isoformat()

            subject = 'UPDATE PASSWORD PIN VERIFICATION'
            template = pin_sender_template(name, pin)
            background_tasks.add_task(emailSender, email, subject, template)  # now `email` is defined
            

            save_pin = db.reference('temporary_keys')
            save_pin.child(user_id).set({
                'generated_pin': pin,
                'expiration_time': expiration_time_str,
                'reference_user_id': user_id  # << ADD THIS too if you want check_db to work properly
            })
        
            return True

        except HTTPException as e:
            print(f"🚨 HTTPException: {e.detail}")
            raise e


        except Exception as e:
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
            )




    @staticmethod
    async def change_password_verify_pin(pin: str, email: str):
        try:
            try:
                user = auth.get_user_by_email(email)
            except Exception:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email not registered"
                )

            user_id = user.uid
            temp_data_ref = db.reference(f'temporary_keys/{user_id}')
            temp_data = temp_data_ref.get()

            if not temp_data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No PIN data found for this user"
                )

            stored_pin = temp_data.get("generated_pin")
            expiration_timestamp = temp_data.get("expiration_time")

            if not stored_pin or not expiration_timestamp:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid temporary key data structure"
                )

            try:
                expiration_time = datetime.fromisoformat(expiration_timestamp)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid expiration time format"
                )

            current_time = datetime.utcnow()

            if current_time > expiration_time:
                temp_data_ref.delete()
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="PIN has expired"
                )

            if str(stored_pin) == str(pin):
                temp_data_ref.delete()
                return True  


            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect PIN"
            )

        except HTTPException:
            raise  # Let FastAPI handle known HTTP errors

        except Exception as e:
            traceback.print_exc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Internal server error: {str(e)}"
            )


    
async def check_db(user_id):
    ref = db.reference('temporary_keys') 
    result = ref.get()
    if result is None:
        print("No temporary_keys found. Collection doesn't exist yet.")
        return  

    if isinstance(result, dict) and not result:
        print("temporary_keys is empty.")
        return

    if isinstance(result, dict):
        for key, record in result.items():
            print(f"Checking record: {record}")
            if record.get('reference_user_id') == user_id:
                print("PIN ALREADY EXISTS.")
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PIN ALREADY EXISTS.")
    elif isinstance(result, list):
        for record in result:
            if record.get('reference_user_id') == user_id:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PIN ALREADY EXISTS.")