from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func
import enum
from app.database.session import Base


class UserRole(str, enum.Enum):
    OWNER = "owner"
    CLINIC = "clinic"
    WELFARE = "welfare"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.OWNER)
    password_hash = Column(String, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)