from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from database import get_db
import models, schemas
from auth import decrypt_field
from routers.users import get_current_user


router = APIRouter()


def get_current_admin(current_user: models.User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


class VerifyProviderPayload(BaseModel):
    is_verified: bool


class AdminProviderOut(BaseModel):
    id: int
    user_id: int
    name: str
    email: str
    bio: Optional[str] = None
    skills: Optional[str] = None
    hourly_rate: Optional[float] = None
    is_verified: bool
    availability_status: bool
    rating_avg: float
    total_jobs: int
    total_reviews: int
    address: Optional[str] = None
    created_at: Optional[str] = None


class AdminStatsOut(BaseModel):
    total_users: int
    total_homeowners: int
    total_providers: int
    verified_providers: int
    pending_providers: int
    total_bookings: int
    active_bookings: int
    completed_bookings: int


@router.get("/admin/stats", response_model=AdminStatsOut)
def get_admin_stats(
    admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    total_users = db.query(models.User).count()
    total_homeowners = db.query(models.User).filter(models.User.role == "homeowner").count()
    total_providers = db.query(models.Provider).count()
    verified_providers = db.query(models.Provider).filter(models.Provider.is_verified == True).count()
    pending_providers = db.query(models.Provider).filter(models.Provider.is_verified == False).count()
    total_bookings = db.query(models.Booking).count()
    active_bookings = db.query(models.Booking).filter(models.Booking.status.in_(["confirmed", "in_progress", "provider_done"])).count()
    completed_bookings = db.query(models.Booking).filter(models.Booking.status == "completed").count()

    return AdminStatsOut(
        total_users=total_users,
        total_homeowners=total_homeowners,
        total_providers=total_providers,
        verified_providers=verified_providers,
        pending_providers=pending_providers,
        total_bookings=total_bookings,
        active_bookings=active_bookings,
        completed_bookings=completed_bookings,
    )


@router.get("/admin/providers", response_model=List[AdminProviderOut])
def list_admin_providers(
    admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    providers = db.query(models.Provider).join(models.User).all()
    results = []
    for p in providers:
        results.append(AdminProviderOut(
            id=p.id,
            user_id=p.user_id,
            name=p.user.name if p.user else "Unknown",
            email=decrypt_field(p.user.email) if p.user else "",
            bio=p.bio,
            skills=p.skills,
            hourly_rate=p.hourly_rate,
            is_verified=p.is_verified,
            availability_status=p.availability_status,
            rating_avg=p.rating_avg or 0.0,
            total_jobs=p.total_jobs or 0,
            total_reviews=p.total_reviews or 0,
            address=p.user.address if p.user else None,
            created_at=p.user.created_at.isoformat() if p.user and p.user.created_at else None,
        ))
    return results


@router.patch("/admin/providers/{provider_id}/verify", response_model=AdminProviderOut)
def verify_provider(
    provider_id: int,
    payload: VerifyProviderPayload,
    admin: models.User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    provider = db.query(models.Provider).filter(models.Provider.id == provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    provider.is_verified = payload.is_verified
    db.commit()
    db.refresh(provider)

    return AdminProviderOut(
        id=provider.id,
        user_id=provider.user_id,
        name=provider.user.name if provider.user else "Unknown",
        email=decrypt_field(provider.user.email) if provider.user else "",
        bio=provider.bio,
        skills=provider.skills,
        hourly_rate=provider.hourly_rate,
        is_verified=provider.is_verified,
        availability_status=provider.availability_status,
        rating_avg=provider.rating_avg or 0.0,
        total_jobs=provider.total_jobs or 0,
        total_reviews=provider.total_reviews or 0,
        address=provider.user.address if provider.user else None,
        created_at=provider.user.created_at.isoformat() if provider.user and provider.user.created_at else None,
    )
