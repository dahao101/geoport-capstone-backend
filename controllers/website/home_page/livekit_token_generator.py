import jwt
import time
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from fastapi import HTTPException, status
from backend.controllers.website.home_page.fetch_room_id import feth_users_room_id

load_dotenv()

livekit_api = os.getenv('livekit_key')
livekit_secret = os.getenv('livekit_secret')

async def token_generator(user_id, call_type):
    try:
        if not livekit_api or not livekit_secret:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="LiveKit credentials not configured."
            )

        room_data = await feth_users_room_id(user_id)
        if not room_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No room ID found for this user."
            )

        room_id = room_data["data"]
        sources = {
            "audio": ["audio"],
            "video": ["audio", "video"]
        }.get(call_type)

        if not sources:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid call type"
            )

        now = int(time.time())
        ttl = 3600 
        exp = now + ttl

        payload = {
            "jti": f"{user_id}-{now}",
            "iss": livekit_api,
            "sub": str(user_id),
            "nbf": now,
            "exp": exp,
            "video": {
                "roomJoin": True,
                "room": room_id,
                "canPublishSources": sources,
                "canSubscribe": True,
                "canPublishData": True
            }
        }
        token = jwt.encode(payload, livekit_secret, algorithm="HS256")
        return token

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
