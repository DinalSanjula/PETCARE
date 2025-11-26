from db import Base
from sqlalchemy import Column, Integer, ForeignKey, String, Text, Float, Boolean, DateTime,func, text
from sqlalchemy.orm import relationship

class Clinic(Base):
    __tablename__ = "clinics"

    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id",ondelete="CASCADE"),nullable=False, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    phone = Column(String(15), nullable=True)
    address = Column(String(120), nullable=True)
    formatted_address = Column(String(255), nullable=True, index=True)
    profile_pic_url = Column(String(255), nullable=True)
    area_id = Column(Integer, ForeignKey("areas.id", ondelete="SET NULL"), nullable=True, index=True)
    latitude = Column(Float, nullable=True, index=True)
    longitude = Column(Float, nullable=True, index=True)
    is_active = Column(Boolean, default=True, server_default=text("true"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(),nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(),nullable=False)

    owner = relationship("User", back_populates="clinics", passive_deletes=True) #USe passive delete also in owner table
    area = relationship("Area", back_populates="clinics")
    images = relationship("ClinicImage", back_populates="clinic", cascade="all, delete-orphan", passive_deletes=True)


class ClinicImage(Base):
    __tablename__ = "clinic_images"

    id = Column(Integer, primary_key=True)
    clinic_id = Column(Integer, ForeignKey("clinics.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(1024), nullable=True)
    url = Column(String(1000), nullable=False)
    content_type = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    clinic = relationship("Clinic", back_populates="images", passive_deletes=True)

class Area(Base):
    __tablename__ = "areas"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    normalized_name = Column(String(100), nullable=False, index=True, unique=True)
    main_region = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    clinics = relationship("Clinic", back_populates="area", passive_deletes=True)

