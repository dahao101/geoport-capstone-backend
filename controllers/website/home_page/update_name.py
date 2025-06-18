from fastapi import HTTPException, status
from firebase_admin import db

async def update_name(user_id: str, new_name: str,image_url:str):
    print('update name reach')
    try:
        ref = db.reference(f'users/{user_id}')
        
        update_data = {'name': new_name,'image':image_url}
        
        ref.update(update_data)

        updated_name = ref.child('name').get()
        
        if updated_name != new_name:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error: Name update failed.")
        
        return {"message": "Name updated successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_BAD_REQUEST, detail=f"Error: {str(e)}")
