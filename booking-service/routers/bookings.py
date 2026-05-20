from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import BookingCreate, BookingResponse
from services import booking_service

router = APIRouter()


@router.post("/", response_model=BookingResponse, status_code=201)
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    return booking_service.create_booking(
        db, booking.guest_id, booking.itinerary_id, booking.cabin_id, booking.sail_date
    )


@router.get("/guest/{guest_id}", response_model=list[BookingResponse])
def get_guest_bookings(guest_id: int, db: Session = Depends(get_db)):
    return booking_service.get_guest_bookings(db, guest_id)


@router.get("/{booking_id}", response_model=BookingResponse)
def get_booking(booking_id: int, db: Session = Depends(get_db)):
    return booking_service.get_booking(db, booking_id)


@router.delete("/{booking_id}", response_model=BookingResponse)
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    return booking_service.cancel_booking(db, booking_id)
