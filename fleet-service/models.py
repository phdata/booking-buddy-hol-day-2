from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from database import Base
import enum


class ShipClass(str, enum.Enum):
    breakaway = "Breakaway"
    getaway = "Getaway"
    joy = "Joy"
    bliss = "Bliss"
    encore = "Encore"


class ShipStatus(str, enum.Enum):
    active = "active"
    drydock = "drydock"
    retired = "retired"


class CabinCategory(str, enum.Enum):
    interior = "interior"
    ocean_view = "ocean_view"
    balcony = "balcony"
    suite = "suite"


class Ship(Base):
    __tablename__ = "ships"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    imo_number = Column(String, unique=True, nullable=False)
    class_name = Column(SAEnum(ShipClass), nullable=False)
    total_cabins = Column(Integer, nullable=False)
    passenger_capacity = Column(Integer, nullable=False)
    home_port = Column(String, nullable=False)
    status = Column(SAEnum(ShipStatus), nullable=False, default=ShipStatus.active)

    cabins = relationship("Cabin", back_populates="ship")
    sailings = relationship("Sailing", back_populates="ship")


class Cabin(Base):
    __tablename__ = "cabins"

    id = Column(Integer, primary_key=True, index=True)
    ship_id = Column(Integer, ForeignKey("ships.id"), nullable=False)
    cabin_number = Column(String, nullable=False)
    category = Column(SAEnum(CabinCategory), nullable=False)
    deck = Column(Integer, nullable=False)
    max_occupancy = Column(Integer, nullable=False, default=2)
    base_rate_usd = Column(Float, nullable=False)

    ship = relationship("Ship", back_populates="cabins")


class Sailing(Base):
    __tablename__ = "sailings"

    id = Column(Integer, primary_key=True, index=True)
    ship_id = Column(Integer, ForeignKey("ships.id"), nullable=False)
    departure_date = Column(String, nullable=False)
    arrival_date = Column(String, nullable=False)
    departure_port = Column(String, nullable=False)
    arrival_port = Column(String, nullable=False)
    itinerary_name = Column(String, nullable=False)

    ship = relationship("Ship", back_populates="sailings")
