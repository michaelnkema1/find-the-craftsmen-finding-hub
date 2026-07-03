# Find Platform — Setup Guide

## Prerequisites
- Python 3.10+
- PostgreSQL (running locally)
- Node.js (optional, only needed if you run a local static server for the frontend)

---

## 1. PostgreSQL Setup

Connect to PostgreSQL as a superuser and create the database and role:

```bash
# Option A — if you have postgres system user
sudo -u postgres psql

# Option B — if you set a password for postgres
psql -U postgres -h localhost
```

Then inside `psql`:

```sql
CREATE USER find_user WITH PASSWORD 'find2026';
CREATE DATABASE find_db OWNER find_user;
\q
```

---

## 2. Backend Setup

```bash
cd backend

# Copy environment file
cp .env.example .env

# Edit .env with your DB credentials:
# DATABASE_URL=postgresql://find_user:find2026@localhost:5432/find_db

# Install dependencies
pip install -r requirements.txt

# Run seed script (creates tables + demo data; use --force to wipe existing data)
python seed.py --force

# Start the API server
uvicorn main:app --reload --port 8000
```

The API will be live at `http://localhost:8000`  
Swagger docs: `http://localhost:8000/docs`

---

## 3. Frontend Setup

Open the frontend from your browser:

```bash
# Simple option — open directly
xdg-open frontend/index.html

# Better option — serve with a local HTTP server (avoids CORS issues)
cd frontend
python3 -m http.server 3000
# Then open http://localhost:3000
```

---

## 4. Demo Credentials

**Password for all demo accounts: `demo1234`**

| Role | Email |
|---|---|
| Homeowner | sarah@demo.com |
| Homeowner | marcus@demo.com |
| Provider (Plumber) | james@demo.com |
| Provider (Cleaner) | amara@demo.com |
| Provider (Carpenter) | david@demo.com |
| Provider (Electrician) | grace@demo.com |
| Provider (Plumber/Landscaping) | emmanuel@demo.com |

---

## 5. Project Structure

```
find/
├── backend/            FastAPI + SQLAlchemy + PostgreSQL
│   ├── main.py         App entry point
│   ├── models.py       ORM models
│   ├── schemas.py      Pydantic schemas
│   ├── auth.py         JWT + AES-256-GCM + bcrypt
│   ├── routers/        API endpoints
│   └── seed.py         Demo data seeder
│
└── frontend/           Vanilla HTML + CSS + JS
    ├── index.html          Landing page
    └── pages/
        ├── login.html
        ├── register.html
        ├── search.html         Map + discovery (Leaflet.js)
        ├── provider.html       Provider profile + reviews
        ├── booking.html        2-step booking wizard
        ├── homeowner-dash.html Bookings + leave reviews
        └── provider-dash.html  Jobs + earnings + profile
```

---

## Security Notes

- Emails are stored **AES-256-GCM encrypted** in the database
- Passwords use **bcrypt** hashing
- All API sessions use **JWT** tokens (1-day expiry)
- Change `SECRET_KEY` and `AES_KEY` in `.env` before going to production
- Set `CORS_ORIGINS` in `.env` to your frontend URL(s) in production
- Frontend API URL defaults to `http://<hostname>:8000/api/v1`; override with `<meta name="find-api-base" content="...">`
