# Find — Skilled Labour Marketplace

A web platform that connects homeowners with verified nearby skilled handyworkers using real-time GPS location, ratings, and a streamlined booking system.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI (Python) + PostgreSQL |
| Auth | JWT · bcrypt · AES-256-GCM encryption |
| Frontend | Vanilla HTML / CSS / JS · Leaflet.js · Chart.js |
| Maps | OpenStreetMap (Nominatim geocoding) |

---

## Prerequisites

Install the following before starting:

| Tool | Minimum version | Download |
|---|---|---|
| Python | 3.10+ | https://python.org/downloads |
| PostgreSQL | 13+ | https://postgresql.org/download |
| Git | any | https://git-scm.com |

---

## 1. Clone the Repository

```bash
git clone https://github.com/michaelnkema1/find-the-craftsmen-finding-hub
cd find
```

---

## 2. PostgreSQL Setup

### Ubuntu / Debian Linux

```bash
# Install PostgreSQL (if not already installed)
sudo apt update && sudo apt install postgresql postgresql-contrib -y

# Start the service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create the database and user
sudo -u postgres psql <<EOF
CREATE USER find_user WITH PASSWORD 'find2026';
CREATE DATABASE find_db OWNER find_user;
\q
EOF
```

### Other Linux (Fedora / Arch / etc.)

```bash
# Fedora / RHEL
sudo dnf install postgresql-server postgresql-contrib
sudo postgresql-setup --initdb
sudo systemctl start postgresql

# Arch
sudo pacman -S postgresql
sudo -u postgres initdb -D /var/lib/postgres/data
sudo systemctl start postgresql

# Then create DB (same as Ubuntu above):
sudo -u postgres psql -c "CREATE USER find_user WITH PASSWORD 'find2026';"
sudo -u postgres psql -c "CREATE DATABASE find_db OWNER find_user;"
```

### macOS

```bash
# Using Homebrew (recommended)
brew install postgresql@16
brew services start postgresql@16

# Create DB and user
psql postgres -c "CREATE USER find_user WITH PASSWORD 'find2026';"
psql postgres -c "CREATE DATABASE find_db OWNER find_user;"
```

### Windows

1. Download the PostgreSQL installer from https://postgresql.org/download/windows/
2. Run the installer — choose a password for the `postgres` superuser (remember it)
3. Open **pgAdmin** or **SQL Shell (psql)** from the Start Menu
4. In SQL Shell, press Enter to accept defaults until asked for password, then enter yours
5. Run:

```sql
CREATE USER find_user WITH PASSWORD 'find2026';
CREATE DATABASE find_db OWNER find_user;
\q
```

---

## 3. Backend Setup

### Ubuntu / Linux / macOS

```bash
cd backend

# Copy and edit the environment file
cp .env.example .env
nano .env   # or use any text editor
```

Set the `DATABASE_URL` line to:

```
DATABASE_URL=postgresql://find_user:find2026@localhost:5432/find_db
```

```bash
# Create a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Seed the database with demo data
python seed.py

# Start the API server
uvicorn main:app --reload --port 8000
```

### Windows (Command Prompt or PowerShell)

```bat
cd backend

# Copy and edit the environment file
copy .env.example .env
notepad .env
```

Set the `DATABASE_URL` line to:

```
DATABASE_URL=postgresql://find_user:find2026@localhost:5432/find_db
```

```bat
:: Create a virtual environment
python -m venv .venv
.venv\Scripts\activate

:: Install dependencies
pip install -r requirements.txt

:: Seed the database with demo data
python seed.py

:: Start the API server
uvicorn main:app --reload --port 8000
```

> The API is now running at **http://localhost:8000**  
> Interactive docs: **http://localhost:8000/docs**

---

## 4. Frontend Setup

Open a **new terminal window** (keep the backend running):

### Ubuntu / Linux / macOS

```bash
cd frontend
python3 -m http.server 3000
```

### Windows

```bat
cd frontend
python -m http.server 3000
```

Then open your browser and go to: **http://localhost:3000**

---

## 5. Quick Start (Linux / macOS only)

A convenience script is included that starts both servers at once:

```bash
# From the project root
chmod +x start.sh
./start.sh
```

This will:
- Auto-create the Python virtual environment if missing
- Install dependencies
- Free any processes already on ports 8000 / 3000
- Start both servers and print the URLs

> **Windows users:** Run the backend and frontend steps from Section 3 & 4 manually in two separate terminal windows.

---

## 6. Environment Variables

Edit `backend/.env` — copy from `backend/.env.example`:

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://find_user:find2026@localhost:5432/find_db` |
| `SECRET_KEY` | JWT signing secret (change in production) | any long random string |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifespan | `1440` (24 hours) |
| `AES_KEY` | 64 hex chars = 32 bytes for AES-256 encryption | see `.env.example` |

> **Security:** Never commit your real `.env` to Git. The `.gitignore` already excludes it.

---

## 7. Demo Credentials

All demo accounts share the same password: **`demo1234`**

| Role | Email |
|---|---|
| Homeowner | sarah@demo.com |
| Homeowner | marcus@demo.com |
| Provider (Plumber) | james@demo.com |
| Provider (Cleaner) | amara@demo.com |
| Provider (Carpenter) | david@demo.com |
| Provider (Electrician) | grace@demo.com |
| Provider (Plumber / Landscaping) | emmanuel@demo.com |

---

## 8. Project Structure

```
find/
├── start.sh                   # One-command launcher (Linux/macOS)
├── README.md
├── .gitignore
│
├── backend/
│   ├── main.py                # FastAPI app entry point
│   ├── models.py              # SQLAlchemy ORM models
│   ├── schemas.py             # Pydantic request/response schemas
│   ├── auth.py                # JWT + bcrypt + AES-256-GCM
│   ├── database.py            # DB engine & session factory
│   ├── seed.py                # Demo data seeder
│   ├── requirements.txt
│   ├── .env.example           # Template — copy to .env
│   └── routers/
│       ├── users.py           # Register, login, profile
│       ├── providers.py       # GPS search, profile update
│       ├── bookings.py        # Create, list, status workflow
│       └── reviews.py         # Submit & list reviews
│
└── frontend/
    ├── index.html             # Landing page
    ├── assets/
    │   ├── css/main.css       # Dark-mode design system (Space Grotesk)
    │   └── js/
    │       ├── api.js         # Fetch wrapper + UI helpers
    │       └── auth.js        # JWT guard + relative routing
    └── pages/
        ├── login.html
        ├── register.html      # Role picker + GPS/address location picker
        ├── search.html        # Live GPS map + provider discovery
        ├── provider.html      # Profile, ratings, reviews
        ├── booking.html       # 2-step booking wizard
        ├── homeowner-dash.html
        └── provider-dash.html # Earnings chart, job management
```

---

## 9. Common Issues

### `role "username" does not exist` (Linux)
PostgreSQL peer authentication requires a matching OS user. Use the `find_user` credentials over TCP:
```
DATABASE_URL=postgresql://find_user:find2026@localhost:5432/find_db
```

### Port already in use
```bash
# Linux/macOS — find and kill the process on port 8000
lsof -ti tcp:8000 | xargs kill -9
```
On Windows, open Task Manager → find `python.exe` → End Task, or:
```bat
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### `ModuleNotFoundError` on Windows
Make sure you activated the virtual environment first:
```bat
.venv\Scripts\activate
```

### GPS not working in browser
Browsers require **HTTPS or localhost** to access geolocation. The local dev server at `http://localhost:3000` is allowed. Opening `index.html` directly as a `file://` URL will block GPS — use the HTTP server instead.
