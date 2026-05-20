from pydantic import BaseModel, ConfigDict
from models import ShipClass, ShipStatus, CabinCategory


class ShipResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    imo_number: str
    class_name: ShipClass
    total_cabins: int
    passenger_capacity: int
    home_port: str
    status: ShipStatus


class CabinResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ship_id: int
    cabin_number: str
    category: CabinCategory
    deck: int
    max_occupancy: int
    base_rate_usd: float


class SailingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ship_id: int
    departure_date: str
    arrival_date: str
    departure_port: str
    arrival_port: str
    itinerary_name: str
