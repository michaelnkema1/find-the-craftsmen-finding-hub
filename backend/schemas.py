from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime


# ── Auth / Users ──────────────────────────────────────────────────────────────
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    name: str
    role: Literal["homeowner", "provider"]
    phone: Optional[str] = None
    address: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    phone: Optional[str] = None
    address: Optional[str] = None
    location_lat: Optional[float]
    location_lng: Optional[float]
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    location_lat: Optional[float] = None
    location_lng: Optional[float] = None


# ── Providers ─────────────────────────────────────────────────────────────────
class ProviderUpdate(BaseModel):
    bio: Optional[str] = None
    skills: Optional[str] = None
    phone: Optional[str] = None
    hourly_rate: Optional[float] = None
    availability_status: Optional[bool] = None


class ProviderOut(BaseModel):
    id: int
    user_id: int
    name: str
    phone: Optional[str] = None
    bio: Optional[str]
    skills: Optional[str]
    hourly_rate: Optional[float]
    is_verified: bool
    availability_status: bool
    avatar_url: Optional[str]
    rating_avg: float
    total_jobs: int
    total_reviews: int
    location_lat: Optional[float]
    location_lng: Optional[float]
    distance_km: Optional[float] = None

    class Config:
        from_attributes = True


# ── Bookings ──────────────────────────────────────────────────────────────────
class BookingCreate(BaseModel):
    provider_id: int
    service_type: str
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    estimated_hours: Optional[float] = None


class BookingStatusUpdate(BaseModel):
    status: str  # pending|confirmed|in_progress|completed|cancelled


class BookingOut(BaseModel):
    id: int
    homeowner_id: int
    provider_id: int
    service_type: str
    description: Optional[str]
    status: str
    scheduled_at: Optional[datetime]
    estimated_hours: Optional[float]
    total_amount: Optional[float]
    created_at: datetime
    provider_name: Optional[str] = None
    provider_phone: Optional[str] = None
    homeowner_name: Optional[str] = None
    homeowner_phone: Optional[str] = None

    class Config:
        from_attributes = True


# ── Reviews ───────────────────────────────────────────────────────────────────
class ReviewCreate(BaseModel):
    booking_id: int
    provider_id: int
    rating: int   # 1–5
    text: Optional[str] = None


class ReviewOut(BaseModel):
    id: int
    booking_id: int
    homeowner_id: int
    provider_id: int
    rating: int
    text: Optional[str]
    created_at: datetime
    homeowner_name: Optional[str] = None

    class Config:
        from_attributes = True
