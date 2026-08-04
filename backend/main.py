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


def _seed_all_demo_data(force=False):
    db = SessionLocal()
    try:
        # 1. Admin account
        admin_email = "admin@find.com"
        email_idx = hashlib.sha256(admin_email.lower().encode()).hexdigest()
        admin_user = db.query(models.User).filter(models.User.email_index == email_idx).first()
        if not admin_user:
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

        # 2. Demo users & providers
        if db.query(models.Provider).count() == 0 or force:
            if force:
                db.query(models.Review).delete()
                db.query(models.Booking).delete()
                db.query(models.Provider).delete()
                db.query(models.User).filter(models.User.role != "admin").delete()
                db.commit()

            passw = hash_password("demo1234")
            ho1 = models.User(
                email=encrypt_field("sarah@demo.com"),
                email_index=hashlib.sha256(b"sarah@demo.com").hexdigest(),
                password_hash=passw, name="Sarah Johnson", role="homeowner",
                phone="+233 24 555 0192",
                location_lat=5.5491, location_lng=-0.1797
            )
            ho2 = models.User(
                email=encrypt_field("marcus@demo.com"),
                email_index=hashlib.sha256(b"marcus@demo.com").hexdigest(),
                password_hash=passw, name="Marcus Williams", role="homeowner",
                phone="+233 20 555 0184",
                location_lat=5.6057, location_lng=-0.1725
            )
            db.add_all([ho1, ho2])
            db.flush()

            providers_data = [
                ("james@demo.com", "James Okafor", "+233 24 123 4567", 5.6470, -0.1511, "Licensed plumber with 8+ years experience. Expert in pipe installations, leak repairs, and bathroom fittings.", "Plumber,Electrician", 250.0, True, 142),
                ("amara@demo.com", "Amara Diallo", "+233 50 987 6543", 5.5782, -0.1851, "Professional cleaning specialist. Deep cleans, post-construction cleaning, and laundry services available.", "Cleaner,Laundry", 120.0, True, 97),
                ("david@demo.com", "David Torres", "+233 20 456 7890", 5.6698, 0.0166, "Master carpenter and skilled painter. Custom furniture, flooring, and interior painting with 10 years in trade.", "Carpenter,Painter", 300.0, True, 218),
                ("grace@demo.com", "Grace Adeyemi", "+233 27 321 0987", 5.5500, -0.1500, "Certified electrician specializing in smart home installations, wiring, and HVAC maintenance.", "Electrician,HVAC", 350.0, True, 185),
                ("emmanuel@demo.com", "Emmanuel Osei", "+233 54 654 3210", 5.6200, -0.2100, "Expert plumber and landscaping professional. Borehole drilling, drainage systems, and garden design.", "Plumber,Landscaping", 200.0, False, 54),
            ]

            for email, name, phone, lat, lng, bio, skills, rate, ver, jobs in providers_data:
                u = models.User(
                    email=encrypt_field(email),
                    email_index=hashlib.sha256(email.lower().encode()).hexdigest(),
                    password_hash=passw, name=name, role="provider",
                    phone=phone,
                    location_lat=lat, location_lng=lng
                )
                db.add(u)
                db.flush()
                p = models.Provider(
                    user_id=u.id, phone=phone, bio=bio, skills=skills, hourly_rate=rate,
                    is_verified=ver, availability_status=True, total_jobs=jobs,
                    rating_avg=4.8, total_reviews=12
                )
                db.add(p)

            db.commit()
            print("Successfully seeded demo homeowners and providers.")
    except Exception as e:
        db.rollback()
        print("Error during auto seeding:", e)
    finally:
        db.close()


def _init_db_with_retries(max_retries=10, delay=2):
    for attempt in range(1, max_retries + 1):
        try:
            models.Base.metadata.create_all(bind=engine)
            _seed_all_demo_data()
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


@app.get("/api/v1/seed", tags=["Seed"])
@app.post("/api/v1/seed", tags=["Seed"])
def trigger_seed():
    _seed_all_demo_data(force=True)
    return {
        "status": "success",
        "message": "Database seeded successfully!",
        "credentials": {
            "admin": "admin@find.com | admin123",
            "homeowners": ["sarah@demo.com (demo1234)", "marcus@demo.com (demo1234)"],
            "providers": ["james@demo.com (demo1234)", "amara@demo.com (demo1234)", "david@demo.com (demo1234)", "grace@demo.com (demo1234)", "emmanuel@demo.com (demo1234)"]
        }
    }
