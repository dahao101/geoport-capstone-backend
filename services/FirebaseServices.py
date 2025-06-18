from dotenv import load_dotenv
import os
import firebase_admin
from firebase_admin import credentials

load_dotenv()


def initialize_firebase():
    """Initializes Firebase app if not already initialized."""
    firebase_service_key = 'backend/services/geoport-malaybalay-firebase-adminsdk-bhb9k-7f691320c8.json'
    database_url = 'https://geoport-malaybalay-default-rtdb.firebaseio.com/'
    if not firebase_service_key:
        raise ValueError("FIREBASE_SERVICE_KEY_PATH is not set in the .env file.")
    
    cred = credentials.Certificate(firebase_service_key)

    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred, {
            'databaseURL': (database_url)
        })

    print("Firebase initialized successfully.")
