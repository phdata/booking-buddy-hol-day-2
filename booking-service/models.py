from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Enum as SAEnum
from sqlalchemy.orm import relationship
from database import Base
import enum


class CabinCategory(str, enum.Enum):
    interior = "interior"
    ocean_view = "ocean_view"
    balcony = "balcony"
    suite = "suite"


class BookingStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"


class Guest(Base):
    __tablename__ = "guests"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    bookings = relationship("Booking", back_populates="guest")


class Itinerary(Base):
    __tablename__ = "itineraries"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    duration_nights = Column(Integer, nullable=False)
    departure_port = Column(String, nullable=False)
    ship_name = Column(String, nullable=False)
    base_price_usd = Column(Numeric(10, 2), nullable=False)

    bookings = relationship("Booking", back_populates="itinerary")


class Cabin(Base):
    __tablename__ = "cabins"

    id = Column(Integer, primary_key=True, index=True)
    cabin_number = Column(String, nullable=False)
    category = Column(SAEnum(CabinCategory), nullable=False)
    deck = Column(Integer, nullable=False)
    max_occupancy = Column(Integer, nullable=False, default=2)

    bookings = relationship("Booking", back_populates="cabin")


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    guest_id = Column(Integer, ForeignKey("guests.id"), nullable=False)
    itinerary_id = Column(Integer, ForeignKey("itineraries.id"), nullable=False)
    cabin_id = Column(Integer, ForeignKey("cabins.id"), nullable=False)
    sail_date = Column(String, nullable=False)
    status = Column(SAEnum(BookingStatus), nullable=False, default=BookingStatus.confirmed)
    total_price_usd = Column(Numeric(10, 2), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    guest = relationship("Guest", back_populates="bookings")
    itinerary = relationship("Itinerary", back_populates="bookings")
    cabin = relationship("Cabin", back_populates="bookings")
