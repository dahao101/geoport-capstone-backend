from fastapi import HTTPException, status
from firebase_admin import auth,db
import traceback
from backend.services.FirebaseServices import initialize_firebase

initialize_firebase()

async def change_email(user_id: str, new_email: str):
    print('change email reached',new_email)
    try:
        if not new_email or '@' not in new_email:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email format")

        try:
            existing_user = auth.get_user(user_id)
            print(f"Existing user found: {existing_user.email}")
            if existing_user.email == new_email:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Unable to change email. Identical current and new email.")
        except auth.UserNotFoundError:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        try:
            auth.get_user_by_email(new_email)
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The email address is already in use.")
        except auth.UserNotFoundError:
            pass  # New email is not in use

        # Perform the update
        updated_user = auth.update_user(user_id, email=new_email)
        print(f"Email updated successfully: {updated_user.email}")
        await remove_temporary_key(user_id)
        return {"message": "Email updated successfully", "email": updated_user.email}

    # General error handling (catch all exceptions)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")  
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Server error: {str(e)}")




async def remove_temporary_key(user_id):
    try:
        ref = db.reference(f'temporary_keys/{user_id}')
        result = ref.delete()
        print(f"Temporary key for {user_id} removed. Result: {result}")
        return True
    except Exception as e:
        print(f"Failed to remove temporary key: {e}")
        print("Traceback:", traceback.format_exc())  # This will show the full traceback
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")