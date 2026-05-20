from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import CabinResponse
from models import Cabin

router = APIRouter()


@router.get("/", response_model=list[CabinResponse])
def list_cabins(db: Session = Depends(get_db)):
    return db.query(Cabin).all()
