from datetime import date, datetime
from pydantic import BaseModel, ConfigDict
from models import BookingStatus, CabinCategory


class GuestCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str | None = None


class GuestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    first_name: str
    last_name: str
    email: str
    phone: str | None
    created_at: datetime


class ItineraryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    destination: str
    duration_nights: int
    departure_port: str
    ship_name: str
    base_price_usd: float


class CabinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cabin_number: str
    category: CabinCategory
    deck: int
    max_occupancy: int


class BookingCreate(BaseModel):
    guest_id: int
    itinerary_id: int
    cabin_id: int
    sail_date: date


class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guest_id: int
    itinerary_id: int
    cabin_id: int
    sail_date: str
    status: BookingStatus
    total_price_usd: float
    created_at: datetime
