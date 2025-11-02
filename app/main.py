from dotenv import load_dotenv
load_dotenv("app/.env")
from fastapi import FastAPI
from app.views import user_views
from app.views import product_views
from app.views import upload_views
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
# import os


app = FastAPI(
    title="Project BE",
    version="1.0.0",
    contact={
        "name": "Muhammad Rayhanul Ihsan",
        "url": "https://github.com/rayhanul-ihsan",
        "email": "mrayhanulihsan@gmail.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)
# print(os.getenv("CLOUDINARY_CLOUD_NAME"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Register router
app.include_router(user_views.router, prefix="/api/v1", tags=["Users"])
app.include_router(product_views.router, prefix="/api/v1", tags=["Products"])
app.include_router(upload_views.router, prefix="/api/v1", tags=["Files"])
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ✅ Register router upload
# app.include_router(upload_views.router, prefix="/api")
