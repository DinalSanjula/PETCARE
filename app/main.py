from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database.session import init_database, close_database
# from app.routers.auth_router import router as auth_router
# from app.routers.user_router import router as user_router
from app.routers.auth_router import router as auth_router
from app.routers.user_router import router as user_router


app = FastAPI(description="PetCare Service")

# call Included routers
app.include_router(auth_router , prefix="/auth")
app.include_router(user_router , prefix="/users")