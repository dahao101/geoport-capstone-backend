from backend.services.email_sender import emailSender
from backend.services.pin_generator import create_pin 
from fastapi import HTTPException, status,BackgroundTasks
from firebase_admin import auth,db
from fastapi.responses import JSONResponse
from backend.services.FirebaseServices import initialize_firebase
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from backend.services.email_templates.change_phone_number import change_phone_template

initialize_firebase()
executor = ThreadPoolExecutor(1)

class ChangeNumber:
    def __init__(self, number: str = "", user_id: str = ""):
        self.number = number
        self.user_id = user_id

    def update_data(self, number: str, user_id: str):
        self.number = number
        self.user_id = user_id

    async def get_user_data(self, id):
        try:
            user = auth.get_user(id)
            return {
                "uid": user.uid,
                "email": user.email,
                "name": user.display_name,
            }
        except auth.UserNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    async def send_verification_pin(self, background_task: BackgroundTasks) -> bool:
        pin, expiration_time = create_pin() 
        print(f"Generated pin: {pin}, expires at: {expiration_time}")
        subject = "Change Your Phone Number"
        user_data = await self.get_user_data(self.user_id)
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        user_realtime_info = await self.get_user()

        if not user_realtime_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found in Realtime Database")
        
        expiration_time_str = expiration_time.isoformat()
        name = user_data["name"]
        email = user_data["email"]
        name = user_realtime_info.get("name")
        template = change_phone_template(pin,name)
        print(f"Sending verification pin to {email}")
        try:
            background_task.add_task(emailSender, email, subject, template)
            save_pin = db.reference(f'temporary_keys')
            data = {'generated_pin': pin,'expiration_time':expiration_time_str}
            save_pin.child(self.user_id).set(data)
            return True 
        except Exception as e:
            print("Failed to send email:", e)
            return False


    async def verify_pin(self, code: str) -> bool:
           try:
                ref = db.reference(f'temporary_keys/{self.user_id}')
                stored_data = ref.get()
                if not stored_data:
                     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Temporary key not found.")
                stored_pin = stored_data.get('generated_pin')
                expiration_time_str = stored_data.get('expiration_time')
    
                if not stored_pin or not expiration_time_str:
                     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing pin or expiration time.")


                print('Stored PIN:', stored_pin)
                print('Inputted PIN:', code)


                checker = await self.checker_function(stored_pin, code)

                if not checker:
                     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The entered PIN does not match the stored PIN.")
    
                if not self.expiration_checker(expiration_time_str):
                     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The expiration time has passed.")

                return True
           except Exception as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")
        
    async def checker_function(self, stored_pin: str, inputted_pin: str) -> bool:
            stored_pin = str(stored_pin).strip()
            inputted_pin = str(inputted_pin).strip()
            print(f"Cleaned Stored PIN: {stored_pin} (type: {type(stored_pin)})")
            print(f"Cleaned Inputted PIN: {inputted_pin} (type: {type(inputted_pin)})")
            try:
                if stored_pin != inputted_pin:
                    print("PINs do not match.")
                    return False
                else:
                    print('PIN matched!')
                    return True
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")


    def expiration_checker(self, expiration_time_str: str) -> bool:
            try:
                expiration_time = datetime.fromisoformat(expiration_time_str)
                current_time = datetime.now()
                if current_time > expiration_time:
                    print("Expiration time has passed.")
                    return False
                else:
                    print("Expiration time is valid.")
                    return True
            except ValueError:
                print("Invalid expiration time format.")
                return False

    async def change_number(self,new_number:str,id:str) -> bool:

        try:
            ref = db.reference(f'users/{id}')
            user_data = ref.get()
            if not user_data:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user not found.")
            ref.update({'contactNumber': new_number,})
            return True
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")

    async def get_user(self):
        ref = db.reference(f'users/{self.user_id}')
        user_data = ref.get()
        if not user_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user_data