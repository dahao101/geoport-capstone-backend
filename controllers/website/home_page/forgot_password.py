from backend.services.email_templates.pin_verification import pin_sender_template
from backend.services.pin_generator import create_pin
from backend.services.email_sender import emailSender
from fastapi import HTTPException, status, BackgroundTasks
from firebase_admin import db, auth
from backend.services.FirebaseServices import initialize_firebase

initialize_firebase()


class forgot_password:

    @staticmethod
    async def forgot_password_send_pin(email: str, background_tasks: BackgroundTasks):
        try:
            user = auth.get_user_by_email(email)

            if not user:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not registered")
            
            user_id = user.uid
            await forgot_password.check_db(user_id) 

            email = user.email
            ref = db.reference(f'users/{user_id}')
            user_data = ref.get()
            name = user_data['name']

            pin, expiration_time = create_pin()
            expiration_time_str = expiration_time.isoformat()

            subject = 'UPDATE PASSWORD PIN VERIFICATION'
            template = pin_sender_template(name, pin)
            background_tasks.add_task(emailSender, email, subject, template)

            save_pin = db.reference('temporary_keys')
            save_pin.child(user_id).set({
                'generated_pin': pin,
                'expiration_time': expiration_time_str,
                'reference_user_id': user_id
            })

            return True

        except auth.UserNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not registered")

        except Exception as e:
            return str(e)

    @staticmethod
    async def check_db(user_id):
        ref = db.reference('temporary_keys') 
        result = ref.get()
        if result is None:
            print("No temporary_keys found.")
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
