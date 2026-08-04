import time
import hashlib
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, SessionLocal
import models
from routers import users, providers, bookings, reviews, admin
from auth import encrypt_field, hash_password

_default_origins = "http://localhost:3000,http://127.0.0.1:3000"
CORS_ORIGINS = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", _default_origins).split(",")
    if o.strip()
]

app = FastAPI(
    title="Find API",
    description="Skilled Labor Marketplace — RESTful API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router,     prefix="/api/v1", tags=["Auth & Users"])
app.include_router(providers.router, prefix="/api/v1", tags=["Providers"])
app.include_router(bookings.router,  prefix="/api/v1", tags=["Bookings"])
app.include_router(reviews.router,   prefix="/api/v1", tags=["Reviews"])
app.include_router(admin.router,     prefix="/api/v1", tags=["Admin"])


def _seed_admin():
    db = SessionLocal()
    try:
        admin_email = "admin@find.com"
        email_idx = hashlib.sha256(admin_email.lower().encode()).hexdigest()
        existing = db.query(models.User).filter(models.User.email_index == email_idx).first()
        if not existing:
            admin_user = models.User(
                email=encrypt_field(admin_email),
                email_index=email_idx,
                password_hash=hash_password("admin123"),
                name="System Administrator",
                role="admin",
            )
            db.add(admin_user)
            db.commit()
            print("Seeded default admin user: admin@find.com / admin123")
    except Exception as e:
        db.rollback()
        print("Error seeding admin user:", e)
    finally:
        db.close()


def _init_db_with_retries(max_retries=10, delay=2):
    for attempt in range(1, max_retries + 1):
        try:
            models.Base.metadata.create_all(bind=engine)
            _seed_admin()
            print("Database initialized successfully.")
            return
        except Exception as e:
            print(f"Database connection attempt {attempt}/{max_retries} failed: {e}")
            if attempt < max_retries:
                time.sleep(delay)


@app.on_event("startup")
def on_startup():
    _init_db_with_retries()


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "Find API v1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
