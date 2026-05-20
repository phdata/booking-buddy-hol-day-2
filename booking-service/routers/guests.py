from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import GuestCreate, GuestResponse
from services import itinerary_service

router = APIRouter()


@router.get("/", response_model=list[GuestResponse])
def list_guests(db: Session = Depends(get_db)):
    return itinerary_service.list_guests(db)


@router.post("/", response_model=GuestResponse, status_code=201)
def create_guest(guest: GuestCreate, db: Session = Depends(get_db)):
    return itinerary_service.create_guest(db, guest.first_name, guest.last_name, guest.email, guest.phone)


@router.get("/{guest_id}", response_model=GuestResponse)
def get_guest(guest_id: int, db: Session = Depends(get_db)):
    return itinerary_service.get_guest(db, guest_id)
