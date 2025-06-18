from fastapi import HTTPException, status
from firebase_admin import auth,db
from backend.services.FirebaseServices import  initialize_firebase

initialize_firebase()


async def fetch_user_data(userId:str):
    try:
        user_info = auth.get_user(userId)
        ref = db.reference(f'users/{userId}')
        user_data = ref.get()


        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User data for {userId} not found in database"
            )
        
        user = auth.get_user(userId)
        email = user.email
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"email for {userId} not found in database"
            )
        
        user_full_data = {
            "userId": user_info.uid,
            "image": user_data.get("image"),
            "name": user_data.get("name"),
            "role": user_data.get("role"),
            "contactNumber": user_data.get("contactNumber"),
            "location": user_data.get("location"), 
            "age": user_data.get("age"),
            "sex": user_data.get("sex"),
            "userType": user_data.get("userType"),
            "status": user_data.get("status"),
            "email":email
        }
        return user_full_data
    
    except auth.UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in Firebase Authentication"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user data: {str(e)}"
        )
