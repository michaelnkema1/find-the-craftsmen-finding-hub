from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from routers.users import get_current_user

router = APIRouter()


def _recalc_rating(provider: models.Provider, db: Session):
    reviews = db.query(models.Review).filter(models.Review.provider_id == provider.id).all()
    provider.total_reviews = len(reviews)
    provider.rating_avg = sum(r.rating for r in reviews) / len(reviews) if reviews else 0.0
    db.commit()


@router.post("/reviews", response_model=schemas.ReviewOut, status_code=201)
def create_review(
    body: schemas.ReviewCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "homeowner":
        raise HTTPException(status_code=403, detail="Only homeowners can leave reviews")
    if not (1 <= body.rating <= 5):
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5")

    booking = db.query(models.Booking).filter(models.Booking.id == body.booking_id).first()
    if not booking or booking.homeowner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Booking not found or not yours")
    if booking.provider_id != body.provider_id:
        raise HTTPException(status_code=400, detail="Provider does not match this booking")
    if booking.status != "completed":
        raise HTTPException(status_code=400, detail="Can only review completed bookings")

    existing = db.query(models.Review).filter(models.Review.booking_id == body.booking_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="You already reviewed this booking")

    review = models.Review(
        booking_id=body.booking_id,
        homeowner_id=current_user.id,
        provider_id=body.provider_id,
        rating=body.rating,
        text=body.text,
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    provider = db.query(models.Provider).filter(models.Provider.id == body.provider_id).first()
    if provider:
        _recalc_rating(provider, db)

    return schemas.ReviewOut(
        id=review.id,
        booking_id=review.booking_id,
        homeowner_id=review.homeowner_id,
        provider_id=review.provider_id,
        rating=review.rating,
        text=review.text,
        created_at=review.created_at,
        homeowner_name=current_user.name,
    )


@router.get("/reviews/provider/{provider_id}", response_model=list[schemas.ReviewOut])
def get_provider_reviews(provider_id: int, db: Session = Depends(get_db)):
    reviews = (
        db.query(models.Review)
        .filter(models.Review.provider_id == provider_id)
        .order_by(models.Review.created_at.desc())
        .all()
    )
    return [
        schemas.ReviewOut(
            id=r.id,
            booking_id=r.booking_id,
            homeowner_id=r.homeowner_id,
            provider_id=r.provider_id,
            rating=r.rating,
            text=r.text,
            created_at=r.created_at,
            homeowner_name=r.homeowner.name if r.homeowner else "Anonymous",
        )
        for r in reviews
    ]
