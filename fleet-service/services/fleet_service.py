from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import Ship, Cabin, Sailing, ShipStatus, CabinCategory


def get_ship(db: Session, ship_id: int) -> Ship:
    ship = db.query(Ship).filter(Ship.id == ship_id).first()
    if not ship:
        raise HTTPException(status_code=404, detail="Ship not found")
    return ship


def list_ships(db: Session, status: ShipStatus | None = None) -> list[Ship]:
    query = db.query(Ship)
    if status:
        query = query.filter(Ship.status == status)
    return query.all()


def get_ship_cabins(db: Session, ship_id: int) -> list[Cabin]:
    get_ship(db, ship_id)
    return db.query(Cabin).filter(Cabin.ship_id == ship_id).all()


def get_available_cabins(
    db: Session,
    ship_id: int,
    category: CabinCategory | None = None,
    limit: int = 50,
) -> list[Cabin]:
    get_ship(db, ship_id)
    query = db.query(Cabin).filter(Cabin.ship_id == ship_id)
    if category:
        query = query.filter(Cabin.category == category)
    return query.all()


def get_sailing(db: Session, sailing_id: int) -> Sailing:
    sailing = db.query(Sailing).filter(Sailing.id == sailing_id).first()
    if not sailing:
        raise HTTPException(status_code=404, detail="Sailing not found")
    return sailing


def list_sailings(db: Session, ship_id: int | None = None, from_date: str | None = None) -> list[Sailing]:
    query = db.query(Sailing)
    if ship_id:
        get_ship(db, ship_id)
        query = query.filter(Sailing.ship_id == ship_id)
    if from_date:
        query = query.filter(Sailing.departure_date >= from_date)
    return query.order_by(Sailing.departure_date).all()
