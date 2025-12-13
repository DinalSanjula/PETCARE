from fastapi import FastAPI
from Clinics.routers.clinic_router import router as clinic_router
from Clinics.routers.clinic_images_router import router as image_router
from Clinics.routers.area_router import router as area_router
from app.routers.user_router import router as user_router
from app.routers.auth_router import router as auth_router

app = FastAPI()

app.include_router(user_router, prefix="/users")
app.include_router(auth_router, prefix="/auth")
app.include_router(area_router, prefix="/areas")
app.include_router(clinic_router, prefix="/clinics")
app.include_router(image_router, prefix="/images")

