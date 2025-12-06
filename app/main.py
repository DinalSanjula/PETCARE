from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database.session import init_database, close_database
from app.routers import auth_router, user_router


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
app.include_router(auth_router.router)
app.include_router(user_router.router)


@app.get("/")
async def root():
    return {"message": "Welcome to PetCare Service API"}