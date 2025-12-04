from db import Base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class User(Base):                      # <-- must match relationship("User")
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(100))

    clinics = relationship("Clinic", back_populates="owner", passive_deletes=True)