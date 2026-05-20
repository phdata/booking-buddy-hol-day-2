from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import SailingResponse
from services import fleet_service

router = APIRouter()


@router.get("/", response_model=list[SailingResponse])
def list_sailings(
    ship_id: int | None = None,
    from_date: str | None = None,
    db: Session = Depends(get_db),
):
    return fleet_service.list_sailings(db, ship_id, from_date)


@router.get("/{sailing_id}", response_model=SailingResponse)
def get_sailing(sailing_id: int, db: Session = Depends(get_db)):
    return fleet_service.get_sailing(db, sailing_id)
