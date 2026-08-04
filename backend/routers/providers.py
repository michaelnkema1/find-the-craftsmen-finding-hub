import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from routers.users import get_current_user

router = APIRouter()


def _haversine_km(lat1, lng1, lat2, lng2) -> float:
    """Great-circle distance between two GPS coordinates in kilometres."""
    R = 6371.0
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlam / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def _build_provider_out(p: models.Provider, user_lat=None, user_lng=None) -> schemas.ProviderOut:
    distance_km = None
    if user_lat is not None and user_lng is not None and p.user.location_lat and p.user.location_lng:
        distance_km = round(_haversine_km(user_lat, user_lng, p.user.location_lat, p.user.location_lng), 2)

    phone_num = p.phone or (p.user.phone if p.user else None)

    return schemas.ProviderOut(
        id=p.id,
        user_id=p.user_id,
        name=p.user.name,
        phone=phone_num,
        bio=p.bio,
        skills=p.skills,
        hourly_rate=p.hourly_rate,
        is_verified=p.is_verified,
        availability_status=p.availability_status,
        avatar_url=p.avatar_url,
        rating_avg=round(p.rating_avg, 1),
        total_jobs=p.total_jobs,
        total_reviews=p.total_reviews,
        location_lat=p.user.location_lat,
        location_lng=p.user.location_lng,
        distance_km=distance_km,
    )


@router.get("/providers", response_model=list[schemas.ProviderOut])
def search_providers(
    lat: Optional[float] = Query(None, description="User latitude"),
    lng: Optional[float] = Query(None, description="User longitude"),
    radius_km: float = Query(25.0, description="Search radius in km"),
    skill: Optional[str] = Query(None, description="Filter by skill keyword"),
    available_only: bool = Query(False),
    db: Session = Depends(get_db),
):
    query = db.query(models.Provider).join(models.User)

    if available_only:
        query = query.filter(models.Provider.availability_status == True)

    if skill:
        query = query.filter(models.Provider.skills.ilike(f"%{skill}%"))

    providers = query.all()

    results = []
    for p in providers:
        if lat is not None and lng is not None and p.user.location_lat and p.user.location_lng:
            d = _haversine_km(lat, lng, p.user.location_lat, p.user.location_lng)
            if d > radius_km:
                continue
        results.append(_build_provider_out(p, lat, lng))

    results.sort(key=lambda x: (x.distance_km or 999))
    return results


@router.get("/providers/{provider_id}", response_model=schemas.ProviderOut)
def get_provider(
    provider_id: int,
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
    db: Session = Depends(get_db),
):
    p = db.query(models.Provider).filter(models.Provider.id == provider_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Provider not found")
    return _build_provider_out(p, lat, lng)


@router.patch("/providers/{provider_id}", response_model=schemas.ProviderOut)
def update_provider(
    provider_id: int,
    body: schemas.ProviderUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    p = db.query(models.Provider).filter(models.Provider.id == provider_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Provider not found")
    if p.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    for field, value in body.model_dump(exclude_unset=True).items():
        if field == "phone":
            setattr(p, "phone", value)
            if p.user:
                setattr(p.user, "phone", value)
        else:
            setattr(p, field, value)
    db.commit()
    db.refresh(p)
    return _build_provider_out(p)
