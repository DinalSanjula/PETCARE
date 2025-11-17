from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import init_database, close_pool
from user_router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print('app is starting')
    await init_database() #app start logic
    yield
    await close_pool()


app = FastAPI(
    title="user service with Database Integration",
    lifespan= lifespan
)

app.include_router(router=router)