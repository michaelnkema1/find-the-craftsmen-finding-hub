from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from routers.users import get_current_user

router = APIRouter()

HOMEOWNER_TRANSITIONS = {
    "pending": {"cancelled"},
    "confirmed": {"cancelled"},
}
PROVIDER_TRANSITIONS = {
    "pending": {"confirmed", "cancelled"},
    "confirmed": {"in_progress", "cancelled"},
    "in_progress": {"completed"},
}


def _booking_out(b: models.Booking) -> schemas.BookingOut:
    return schemas.BookingOut(
        id=b.id,
        homeowner_id=b.homeowner_id,
        provider_id=b.provider_id,
        service_type=b.service_type,
        description=b.description,
        status=b.status,
        scheduled_at=b.scheduled_at,
        estimated_hours=b.estimated_hours,
        total_amount=b.total_amount,
        created_at=b.created_at,
        provider_name=b.provider.user.name if b.provider and b.provider.user else None,
        homeowner_name=b.homeowner.name if b.homeowner else None,
    )


@router.post("/bookings", response_model=schemas.BookingOut, status_code=201)
def create_booking(
    body: schemas.BookingCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "homeowner":
        raise HTTPException(status_code=403, detail="Only homeowners can create bookings")

    provider = db.query(models.Provider).filter(models.Provider.id == body.provider_id).first()
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")

    total = None
    if provider.hourly_rate and body.estimated_hours:
        total = round(provider.hourly_rate * body.estimated_hours, 2)

    booking = models.Booking(
        homeowner_id=current_user.id,
        provider_id=body.provider_id,
        service_type=body.service_type,
        description=body.description,
        scheduled_at=body.scheduled_at,
        estimated_hours=body.estimated_hours,
        total_amount=total,
        status="pending",
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return _booking_out(booking)


@router.get("/bookings", response_model=list[schemas.BookingOut])
def list_bookings(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role == "homeowner":
        bookings = (
            db.query(models.Booking)
            .filter(models.Booking.homeowner_id == current_user.id)
            .order_by(models.Booking.created_at.desc())
            .all()
        )
    else:
        provider = db.query(models.Provider).filter(models.Provider.user_id == current_user.id).first()
        if not provider:
            return []
        bookings = (
            db.query(models.Booking)
            .filter(models.Booking.provider_id == provider.id)
            .order_by(models.Booking.created_at.desc())
            .all()
        )
    return [_booking_out(b) for b in bookings]


@router.patch("/bookings/{booking_id}/status", response_model=schemas.BookingOut)
def update_booking_status(
    booking_id: int,
    body: schemas.BookingStatusUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    allowed = {"pending", "confirmed", "in_progress", "completed", "cancelled"}
    if body.status not in allowed:
        raise HTTPException(status_code=400, detail=f"Status must be one of {allowed}")

    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if body.status == booking.status:
        return _booking_out(booking)

    # Authorization and allowed status transitions
    if current_user.role == "homeowner":
        if booking.homeowner_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        allowed = HOMEOWNER_TRANSITIONS.get(booking.status, set())
        if body.status not in allowed:
            raise HTTPException(status_code=400, detail=f"Homeowners cannot set status to '{body.status}' from '{booking.status}'")
    elif current_user.role == "provider":
        provider = db.query(models.Provider).filter(models.Provider.user_id == current_user.id).first()
        if not provider or booking.provider_id != provider.id:
            raise HTTPException(status_code=403, detail="Not authorized")
        allowed = PROVIDER_TRANSITIONS.get(booking.status, set())
        if body.status not in allowed:
            raise HTTPException(status_code=400, detail=f"Providers cannot set status to '{body.status}' from '{booking.status}'")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    previous_status = booking.status
    booking.status = body.status

    if body.status == "completed" and previous_status != "completed":
        booking.provider.total_jobs += 1

    db.commit()
    db.refresh(booking)
    return _booking_out(booking)
