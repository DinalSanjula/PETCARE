from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime, timezone
import enum


# Helper function for datetime defaults
def utc_now():
    return datetime.now(timezone.utc)

# Database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./petcare.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Status enum for reports
class ReportStatus(str, enum.Enum):
    new = "new"
    in_progress = "in_progress"
    resolved = "resolved"


# User roles enum
class UserRole(str, enum.Enum):
    admin = "admin"
    ngo = "ngo"


# User model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default=UserRole.ngo.value)
    created_at = Column(DateTime, default=utc_now)
    
    # Relationship to organization
    organization = relationship("Organization", back_populates="user", uselist=False)


# Organization model
class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(String)
    is_verified = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=utc_now)
    
    # Relationship to user
    user = relationship("User", back_populates="organization")
    # Relationship to reports
    reports = relationship("AnimalReport", back_populates="organization")


# Animal Report model
class AnimalReport(Base):
    __tablename__ = "animal_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    location = Column(String)
    status = Column(String, default=ReportStatus.new.value)
    organization_id = Column(Integer, ForeignKey("organizations.id"))
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    
    # Relationship to organization
    organization = relationship("Organization", back_populates="reports")


# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)


# Get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

