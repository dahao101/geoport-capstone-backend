import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import cloudinary.api
import shutil
from tempfile import NamedTemporaryFile
import asyncio
from concurrent.futures import ThreadPoolExecutor

load_dotenv(dotenv_path='backend/.env')

cloud_name = os.getenv('CLOUD_NAME')
api_key = os.getenv('CLOUDINARY_API_KEY')
secret_key = os.getenv('CLOUDINARY_SECRET_KEY')

cloudinary.config(
    cloud_name=cloud_name,
    api_key=api_key,
    api_secret=secret_key
)

def folder_exists(user_id):
    try:
        resources = cloudinary.api.resources(prefix=f"PROFILE IMAGES/{user_id}/", type="upload", max_results=1)
        return len(resources['resources']) > 0
    except Exception as e:
        print(f"Error checking if folder exists: {str(e)}")
        return False

def delete_images_in_folder(user_id):
    try:
        resources = cloudinary.api.resources(prefix=f"PROFILE IMAGES/{user_id}/", type="upload", max_results=500)
        
        if not resources['resources']:
            print(f"No images found in folder for user {user_id}. No deletion needed.")
            return
        
        for resource in resources['resources']:
            public_id = resource.get('public_id')
            if public_id:
                cloudinary.uploader.destroy(public_id)
                print(f"Deleted image with public_id: {public_id}")
            else:
                print(f"Public ID not found for resource: {resource}")
    except Exception as e:
        print(f"Error deleting images: {str(e)}")

def sync_upload(image_path, folder_name):
    try:
        upload_result = cloudinary.uploader.upload(image_path, folder=f"PROFILE IMAGES/{folder_name}")
        print(f"Upload result: {upload_result}")
        return upload_result['secure_url']
    except Exception as e:
        print(f"Error uploading image to Cloudinary: {str(e)}")
        return None

async def cloudinary_uploader(image, user_id):
    folder_name = str(user_id) 

    if not folder_exists(user_id):
        print(f"Folder for user {user_id} does not exist. A new folder will be created.")
    
    delete_images_in_folder(user_id)
    
    try:
        with NamedTemporaryFile(delete=False) as temp_file:
            temp_filename = temp_file.name
            with open(temp_filename, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            image_url = await loop.run_in_executor(pool, sync_upload, temp_filename, folder_name)

        os.remove(temp_filename)
        
        return image_url
    
    except Exception as e:
        print(f"Error uploading image to Cloudinary: {str(e)}")
        return None
