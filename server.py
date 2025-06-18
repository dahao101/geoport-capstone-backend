import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.websiteRoutes.loginpage import router as loginpage_router
from backend.routes.websiteRoutes.homepage import router as homepage_router
from backend.routes.applicationRoutes.homepage import router as app_homepage
from backend.routes.applicationRoutes.responder import router as responder_router
from backend.services.fetch_ip import get_ip
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()




allow_origins = [
    "http://localhost:5173",
    "http://172.28.144.1:5173",
    "http://10.255.1.214:5173",
    "http://10.0.2.2:5173"
]


app.add_middleware(
    CORSMiddleware, 
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

 
app.include_router(loginpage_router,prefix="/admin/landing_page" , tags=["Admin"])
app.include_router(homepage_router , prefix="/admin/home_page" , tags=["Admin"])

app.include_router(app_homepage,prefix="/application/home_page", tags=["User"])
app.include_router(responder_router,prefix="/responder_application/home_page", tags=["Responder"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8001)))