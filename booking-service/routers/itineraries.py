from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import ItineraryResponse
from services import itinerary_service

router = APIRouter()


@router.get("/", response_model=list[ItineraryResponse])
def list_itineraries(
    destination: str | None = None,
    min_nights: int | None = None,
    max_nights: int | None = None,
    db: Session = Depends(get_db),
):
    return itinerary_service.search_itineraries(db, destination, min_nights, max_nights)


@router.get("/{itinerary_id}", response_model=ItineraryResponse)
def get_itinerary(itinerary_id: int, db: Session = Depends(get_db)):
    return itinerary_service.get_itinerary(db, itinerary_id)
