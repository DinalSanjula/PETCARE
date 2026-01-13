from fastapi import FastAPI
from Clinics.routers.clinic_router import router as clinic_router
from Clinics.routers.clinic_images_router import router as image_router
from Clinics.routers.area_router import router as area_router
from Users.routers.user_router import router as user_router
from Users.routers.auth_router import router as auth_router
from Admin.admin_users import router as user_admin
from Admin.admin_clinics import router as clinic_admin
from Admin.admin_stats_router import router as admin_stats_router
from Admin.admin_health import router as admin_health_router
from Appointments.router.booking_router import router as booking_router
from Reports.routers.reports_router import router as report_router
from Reports.routers.report_messages import router as report_messages_router
from Notification.router.notification_router import router as notification_router
from Appointments.router.stats_router import router as stats_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",   # VS Code Live Server
        "http://127.0.0.1:5500",
        "http://localhost:3000",   # if needed later
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router, prefix="/users")
app.include_router(auth_router, prefix="/auth")
app.include_router(user_admin, prefix="/admin/users")
app.include_router(clinic_admin, prefix="/admin/clinics")
app.include_router(area_router, prefix="/areas")
app.include_router(clinic_router, prefix="/clinics")
app.include_router(image_router, prefix="/images")
app.include_router(admin_stats_router, prefix="/admin/stats")
app.include_router(admin_health_router, prefix="/admin/health")
app.include_router(booking_router, prefix="/appointments")
app.include_router(report_router, prefix="/reports")
app.include_router(report_messages_router, prefix="/reports")
app.include_router(notification_router, prefix="/notifications")
app.include_router(stats_router)