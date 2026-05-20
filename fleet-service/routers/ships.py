from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from schemas import ShipResponse, CabinResponse
from models import ShipStatus, CabinCategory
from services import fleet_service

router = APIRouter()


@router.get("/", response_model=list[ShipResponse])
def list_ships(status: ShipStatus | None = None, db: Session = Depends(get_db)):
    return fleet_service.list_ships(db, status)


@router.get("/{ship_id}", response_model=ShipResponse)
def get_ship(ship_id: int, db: Session = Depends(get_db)):
    return fleet_service.get_ship(db, ship_id)


@router.get("/{ship_id}/cabins", response_model=list[CabinResponse])
def get_ship_cabins(ship_id: int, db: Session = Depends(get_db)):
    return fleet_service.get_ship_cabins(db, ship_id)


@router.get("/{ship_id}/cabins/available", response_model=list[CabinResponse])
def get_available_cabins(
    ship_id: int,
    category: CabinCategory | None = None,
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return fleet_service.get_available_cabins(db, ship_id, category, limit)
