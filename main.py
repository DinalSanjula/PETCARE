from fastapi import FastAPI
from Clinics.routers.clinic_router import router as clinic_router
from Clinics.routers.clinic_images_router import router as image_router
from Clinics.routers.area_router import router as area_router

app = FastAPI()

# Include routers
app.include_router(clinic_router, prefix="/clinics")
app.include_router(image_router, prefix="/images")
app.include_router(area_router, prefix="/areas")
