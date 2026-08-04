import hashlib
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from auth import (
    encrypt_field, decrypt_field,
    hash_password, verify_password,
    create_access_token, decode_access_token,
)

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")


def _email_index(email: str) -> str:
    """Deterministic SHA-256 hash used to look up encrypted email rows."""
    return hashlib.sha256(email.lower().encode()).hexdigest()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    try:
        user_id = int(payload.get("sub"))
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _user_out(user: models.User) -> schemas.UserOut:
    return schemas.UserOut(
        id=user.id,
        name=user.name,
        email=decrypt_field(user.email),
        role=user.role,
        phone=user.phone,
        address=user.address,
        location_lat=user.location_lat,
        location_lng=user.location_lng,
        created_at=user.created_at,
    )


def _authenticate(email: str, password: str, db: Session) -> models.User:
    idx = _email_index(email)
    user = db.query(models.User).filter(models.User.email_index == idx).first()
    if not user or not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user


@router.post("/auth/register", response_model=schemas.Token, status_code=201)
def register(body: schemas.UserRegister, db: Session = Depends(get_db)):
    idx = _email_index(body.email)
    if db.query(models.User).filter(models.User.email_index == idx).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = models.User(
        email=encrypt_field(body.email),
        email_index=idx,
        password_hash=hash_password(body.password),
        name=body.name,
        role=body.role,
        phone=body.phone,
        address=body.address,
        location_lat=body.location_lat,
        location_lng=body.location_lng,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    if body.role == "provider":
        provider = models.Provider(user_id=user.id)
        db.add(provider)
        db.commit()

    token = create_access_token({"sub": str(user.id)})
    return schemas.Token(
        access_token=token,
        token_type="bearer",
        user=_user_out(user),
    )


@router.post("/auth/login", response_model=schemas.Token)
def login(body: schemas.UserLogin, db: Session = Depends(get_db)):
    user = _authenticate(body.email, body.password, db)
    token = create_access_token({"sub": str(user.id)})
    return schemas.Token(
        access_token=token,
        token_type="bearer",
        user=_user_out(user),
    )


@router.post("/auth/token", response_model=schemas.Token)
def login_form(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """OAuth2-compatible login for Swagger / API clients (username = email)."""
    user = _authenticate(form.username, form.password, db)
    token = create_access_token({"sub": str(user.id)})
    return schemas.Token(
        access_token=token,
        token_type="bearer",
        user=_user_out(user),
    )


@router.get("/users/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    return _user_out(current_user)


@router.patch("/users/me", response_model=schemas.UserOut)
def update_me(
    body: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return _user_out(current_user)
