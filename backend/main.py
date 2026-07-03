from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine
import models
import os

# Create all tables
models.Base.metadata.create_all(bind=engine)

from routers import users, providers, bookings, reviews

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


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "service": "Find API v1.0.0"}


@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy"}
