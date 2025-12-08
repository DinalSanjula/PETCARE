from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database.session import init_database, close_database
from app.routers.auth_router import router as auth_router
from app.routers.user_router import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("App is starting...")
    await init_database()
    yield
    await close_database()
    print("App is shutdown...")


app = FastAPI(
    title="PetCare Service",
    description="PetCare management system",
    lifespan=lifespan
)

# call Included routers
app.include_router(auth_router,prefix="/auth")
app.include_router(user_router,prefix="/user")


@app.get("/")
async def root():
    return {"message": "Welcome to PetCare Service API"}