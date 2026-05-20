from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import bookings, itineraries, guests, cabins


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Fleet Ops — Booking Service", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(bookings.router, prefix="/bookings", tags=["Bookings"])
app.include_router(itineraries.router, prefix="/itineraries", tags=["Itineraries"])
app.include_router(guests.router, prefix="/guests", tags=["Guests"])
app.include_router(cabins.router, prefix="/cabins", tags=["Cabins"])
