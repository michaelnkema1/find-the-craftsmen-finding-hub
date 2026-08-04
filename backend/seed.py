"""
Seed script — populates the database with demo users, providers, bookings, and reviews.
Run from the backend/ directory:
    python seed.py

Demo credentials (all passwords: demo1234):
  Homeowners : sarah@demo.com | marcus@demo.com
  Providers  : james@demo.com | amara@demo.com | david@demo.com | grace@demo.com | emmanuel@demo.com
"""
import sys
import hashlib
import argparse
from datetime import datetime, timedelta, timezone

sys.path.insert(0, ".")  # ensure local imports work
from database import SessionLocal, engine
import models
from auth import encrypt_field, hash_password

parser = argparse.ArgumentParser(description="Seed the Find database with demo data.")
parser.add_argument(
    "--force",
    action="store_true",
    help="Drop and recreate all tables (destroys existing data).",
)
args = parser.parse_args()

if args.force:
    models.Base.metadata.drop_all(bind=engine)
    print("⚠  Dropped all tables (--force)")
else:
    db_check = SessionLocal()
    try:
        if db_check.query(models.User).count() > 0:
            print("Database already has data. Run with --force to wipe and re-seed.")
            sys.exit(0)
    finally:
        db_check.close()

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()

PASSWORD = "demo1234"

# ── Helpers ───────────────────────────────────────────────────────────────────
def email_index(email: str) -> str:
    return hashlib.sha256(email.lower().encode()).hexdigest()


def make_user(email, name, phone, role, lat, lng) -> models.User:
    return models.User(
        email=encrypt_field(email),
        email_index=email_index(email),
        password_hash=hash_password(PASSWORD),
        name=name,
        phone=phone,
        role=role,
        location_lat=lat,
        location_lng=lng,
    )


# ── Seed data ─────────────────────────────────────────────────────────────────
HOMEOWNERS = [
    ("sarah@demo.com",   "Sarah Johnson",   "+233 24 555 0192", 5.5491, -0.1797),  # Osu, Accra
    ("marcus@demo.com",  "Marcus Williams", "+233 20 555 0184", 5.6057, -0.1725),  # Airport Residential, Accra
]

PROVIDERS = [
    {
        "email": "james@demo.com", "name": "James Okafor", "phone": "+233 24 123 4567",
        "lat": 5.6470, "lng": -0.1511,  # East Legon, Accra
        "bio": "Licensed plumber with 8+ years experience. Expert in pipe installations, leak repairs, and bathroom fittings.",
        "skills": "Plumber,Electrician",
        "rate": 250.0, "verified": True, "jobs": 142,
    },
    {
        "email": "amara@demo.com", "name": "Amara Diallo", "phone": "+233 50 987 6543",
        "lat": 5.5782, "lng": -0.1851,  # Cantonments, Accra
        "bio": "Professional cleaning specialist. Deep cleans, post-construction cleaning, and laundry services available.",
        "skills": "Cleaner,Laundry",
        "rate": 120.0, "verified": True, "jobs": 97,
    },
    {
        "email": "david@demo.com", "name": "David Torres", "phone": "+233 20 456 7890",
        "lat": 5.6698, "lng": 0.0166,   # Tema, Greater Accra
        "bio": "Master carpenter and skilled painter. Custom furniture, flooring, and interior painting with 10 years in the trade.",
        "skills": "Carpenter,Painter",
        "rate": 300.0, "verified": True, "jobs": 218,
    },
    {
        "email": "grace@demo.com", "name": "Grace Adeyemi", "phone": "+233 27 321 0987",
        "lat": 5.5500, "lng": -0.1500,  # Labadi, Accra
        "bio": "Certified electrician specializing in smart home installations, wiring, and HVAC maintenance.",
        "skills": "Electrician,HVAC",
        "rate": 350.0, "verified": True, "jobs": 185,
    },
    {
        "email": "emmanuel@demo.com", "name": "Emmanuel Osei", "phone": "+233 54 654 3210",
        "lat": 5.6200, "lng": -0.2100,  # Achimota, Accra
        "bio": "Expert plumber and landscaping professional. Borehole drilling, drainage systems, and garden design.",
        "skills": "Plumber,Landscaping",
        "rate": 200.0, "verified": False, "jobs": 54,
    },
]

REVIEW_TEXTS = [
    "Absolutely fantastic work! Showed up on time, fixed the issue quickly, and left the place spotless.",
    "Very professional and skilled. Would definitely hire again.",
    "Great service! Communicated clearly and finished the job ahead of schedule.",
    "Quality work at a fair price. Highly recommended.",
    "Reliable and thorough. No complaints at all!",
    "Did an excellent job. Very detail-oriented and clean.",
    "Arrived promptly, assessed the issue quickly, and resolved it with minimal disruption.",
    "Polite, efficient, and great value for money.",
]

print("Seeding database...")

# Clear existing seed data
db.query(models.Review).delete()
db.query(models.Booking).delete()
db.query(models.Provider).delete()
db.query(models.User).delete()
db.commit()

# Create Admin
admin_email = "admin@find.com"
admin_user = models.User(
    email=encrypt_field(admin_email),
    email_index=email_index(admin_email),
    password_hash=hash_password("admin123"),
    name="System Administrator",
    phone="+233 30 000 0000",
    role="admin",
)
db.add(admin_user)
db.flush()
print(f"  + Admin:     System Administrator <{admin_email}>")

# Create homeowners
ho_users = []
for email, name, phone, lat, lng in HOMEOWNERS:
    u = make_user(email, name, phone, "homeowner", lat, lng)
    db.add(u)
    db.flush()
    ho_users.append(u)
    print(f"  + Homeowner: {name} <{email}>")

# Create providers
prov_records = []
for i, p_data in enumerate(PROVIDERS):
    u = make_user(p_data["email"], p_data["name"], p_data["phone"], "provider", p_data["lat"], p_data["lng"])
    db.add(u)
    db.flush()

    prov = models.Provider(
        user_id=u.id,
        phone=p_data["phone"],
        bio=p_data["bio"],
        skills=p_data["skills"],
        hourly_rate=p_data["rate"],
        is_verified=p_data["verified"],
        availability_status=True,
        total_jobs=p_data["jobs"],
    )
    db.add(prov)
    db.flush()
    prov_records.append((u, prov))
    print(f"  + Provider:  {p_data['name']} <{p_data['email']}>")

db.commit()

# Create completed bookings + reviews for each provider
for idx, (prov_user, prov) in enumerate(prov_records):
    ratings = []
    for j, ho_user in enumerate(ho_users):
        sched = datetime.now(timezone.utc) - timedelta(days=30 - idx * 5 - j * 2)
        booking = models.Booking(
            homeowner_id=ho_user.id,
            provider_id=prov.id,
            service_type=prov.skills.split(",")[0],
            description="Service requested via demo seed.",
            status="completed",
            scheduled_at=sched,
            estimated_hours=3.0,
            total_amount=round(prov.hourly_rate * 3, 2),
        )
        db.add(booking)
        db.flush()

        rating = 4 + (idx + j) % 2  # alternates between 4 and 5
        ratings.append(rating)
        review = models.Review(
            booking_id=booking.id,
            homeowner_id=ho_user.id,
            provider_id=prov.id,
            rating=rating,
            text=REVIEW_TEXTS[(idx * len(ho_users) + j) % len(REVIEW_TEXTS)],
            created_at=sched + timedelta(hours=4),
        )
        db.add(review)

    db.flush()
    prov.total_reviews = len(ratings)
    prov.rating_avg = round(sum(ratings) / len(ratings), 1)

db.commit()
print("\n✅ Seed complete!")
print("\nDemo credentials:")
print("  Admin      : admin@find.com | admin123")
print("  Homeowners : sarah@demo.com | marcus@demo.com (password: demo1234)")
print("  Providers  : james@demo.com | amara@demo.com | david@demo.com | grace@demo.com | emmanuel@demo.com (password: demo1234)")
