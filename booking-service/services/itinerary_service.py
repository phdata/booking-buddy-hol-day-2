from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Itinerary, Guest


def get_itinerary(db: Session, itinerary_id: int) -> Itinerary:
    itinerary = db.query(Itinerary).filter(Itinerary.id == itinerary_id).first()
    if not itinerary:
        raise HTTPException(status_code=404, detail="Itinerary not found")
    return itinerary


def list_itineraries(db: Session, destination: str | None = None) -> list[Itinerary]:
    query = db.query(Itinerary)
    if destination:
        query = query.filter(Itinerary.destination.ilike(f"%{destination}%"))
    return query.all()


def search_itineraries(
    db: Session,
    destination: str | None = None,
    min_nights: int | None = None,
    max_nights: int | None = None,
) -> list[Itinerary]:
    query = db.query(Itinerary)
    if destination:
        query = query.filter(Itinerary.destination.ilike(f"%{destination}%"))
    if min_nights is not None:
        query = query.filter(Itinerary.duration_nights >= min_nights)
    if max_nights is not None:
        query = query.filter(Itinerary.duration_nights <= max_nights)
    return query.all()


def list_guests(db: Session) -> list[Guest]:
    return db.query(Guest).all()


def get_guest(db: Session, guest_id: int) -> Guest:
    guest = db.query(Guest).filter(Guest.id == guest_id).first()
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found")
    return guest


def create_guest(db: Session, first_name: str, last_name: str, email: str, phone: str | None) -> Guest:
    existing = db.query(Guest).filter(Guest.email == email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Guest with this email already exists")
    guest = Guest(first_name=first_name, last_name=last_name, email=email, phone=phone)
    db.add(guest)
    db.commit()
    db.refresh(guest)
    return guest
