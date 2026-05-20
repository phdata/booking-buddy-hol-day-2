from datetime import date
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Booking, BookingStatus, CabinCategory

CABIN_UPLIFT = {
    CabinCategory.interior: Decimal("0.00"),
    CabinCategory.ocean_view: Decimal("150.00"),
    CabinCategory.balcony: Decimal("300.00"),
    CabinCategory.suite: Decimal("750.00"),
}


def create_booking(db: Session, guest_id: int, itinerary_id: int, cabin_id: int, sail_date: date) -> Booking:
    from models import Guest, Itinerary, Cabin

    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")

    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")

    cabin = db.query(Cabin).filter(Cabin.id == cabin_id).first()
    if not cabin:
        raise HTTPException(status_code=404, detail="Cabin not found")

    sail_date_str = sail_date.isoformat()
    conflict = (
        db.query(Booking)
        .filter(
            Booking.cabin_id == cabin_id,
            Booking.sail_date == sail_date_str,
            Booking.status != BookingStatus.cancelled,
        )
        .first()
    )
    if conflict:
        raise HTTPException(status_code=409, detail="Cabin already booked for this sailing date")

    total_price = itinerary.base_price_usd + CABIN_UPLIFT.get(cabin.category, 0.0)

    booking = Booking(
        guest_id=guest_id,
        itinerary_id=itinerary_id,
        cabin_id=cabin_id,
        sail_date=sail_date_str,
        status=BookingStatus.confirmed,
        total_price_usd=total_price,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def cancel_booking(db: Session, booking_id: int) -> Booking:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = BookingStatus.cancelled
    db.commit()
    db.refresh(booking)
    return booking


def get_booking(db: Session, booking_id: int) -> Booking:
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


def get_guest_bookings(db: Session, guest_id: int) -> list[Booking]:
    from models import Guest

    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    return (
        db.query(Booking)
        .filter(Booking.guest_id == guest_id, Booking.status != BookingStatus.cancelled)
        .all()
    )
