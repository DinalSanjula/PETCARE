from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from database import Base, engine
from routers import reports

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="PetCare API", description="API for PetCare Application", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(reports.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to PetCare API"}
