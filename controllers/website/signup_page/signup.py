import os
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth

load_dotenv()
cred = credentials.Certificate('backend/services/geoport-malaybalay-firebase-adminsdk-bhb9k-7f691320c8.json')
firebase_admin.initialize_app(cred)

def createAccount():
    print()