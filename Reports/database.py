from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Using sqlite for local dev as no MySQL creds provided yet, but easy to switch.
# User mentioned MySQL, so I will prepare for it but default to sqlite for immediate runnability if they don't have mysql running.
# Actually, the user specifically mentioned MySQL in the prompt ("MySQL indexing basics").
# I will use a placeholder MySQL URL or SQLite with a comment.
# Given I can't ask for creds easily without stopping, I will use SQLite for now to ensure it works, 
# and add a comment to swap to MySQL.

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://user:password@localhost/dbname"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
