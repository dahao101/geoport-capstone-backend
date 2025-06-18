from firebase_admin import auth,exceptions
from fastapi import HTTPException, status
from backend.services.FirebaseServices import initialize_firebase

initialize_firebase()

async def update_user_password(email: str, new_password: str):
    try:
        user = auth.get_user_by_email(email)
        auth.update_user(
            uid=user.uid,
            password=new_password
        )
        return {"status": "success", "message": "Password updated successfully"}
    except exceptions.FirebaseError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Firebase error: {str(e)}"
        )


    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
