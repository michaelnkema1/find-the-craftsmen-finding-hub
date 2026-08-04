from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, timezone


def _utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)   # AES-256-GCM encrypted
    email_index = Column(String, unique=True, index=True, nullable=False)  # SHA-256 hash for lookup
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "homeowner" | "provider"
    phone = Column(String, nullable=True)  # Contact phone number
    address = Column(String, nullable=True)   # Human-readable address
    location_lat = Column(Float, nullable=True)
    location_lng = Column(Float, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    provider_profile = relationship("Provider", back_populates="user", uselist=False)
    homeowner_bookings = relationship("Booking", foreign_keys="Booking.homeowner_id", back_populates="homeowner")
    homeowner_reviews = relationship("Review", foreign_keys="Review.homeowner_id", back_populates="homeowner")


class Provider(Base):
    __tablename__ = "providers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    phone = Column(String, nullable=True)           # Direct contact phone number
    bio = Column(Text, nullable=True)
    skills = Column(String, nullable=True)          # Comma-separated: "Plumber,Electrician"
    hourly_rate = Column(Float, nullable=True)
    is_verified = Column(Boolean, default=False)
    availability_status = Column(Boolean, default=True)  # True = available
    avatar_url = Column(String, nullable=True)
    rating_avg = Column(Float, default=0.0)
    total_jobs = Column(Integer, default=0)
    total_reviews = Column(Integer, default=0)

    user = relationship("User", back_populates="provider_profile")
    bookings = relationship("Booking", back_populates="provider")
    reviews = relationship("Review", back_populates="provider")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    homeowner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    service_type = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending|confirmed|in_progress|completed|cancelled
    scheduled_at = Column(DateTime, nullable=True)
    estimated_hours = Column(Float, nullable=True)
    total_amount = Column(Float, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    homeowner = relationship("User", foreign_keys=[homeowner_id], back_populates="homeowner_bookings")
    provider = relationship("Provider", back_populates="bookings")


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (UniqueConstraint("booking_id", name="uq_review_booking"),)

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(Integer, ForeignKey("bookings.id"), nullable=False)
    homeowner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider_id = Column(Integer, ForeignKey("providers.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1–5
    text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow)

    booking = relationship("Booking")
    homeowner = relationship("User", foreign_keys=[homeowner_id], back_populates="homeowner_reviews")
    provider = relationship("Provider", back_populates="reviews")
