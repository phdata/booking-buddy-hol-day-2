from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import LoyaltyAccountResponse, PointsTransactionResponse, AwardPointsRequest, RedeemPointsRequest
from services import loyalty_service

router = APIRouter()


@router.get("/{guest_id}", response_model=LoyaltyAccountResponse)
def get_account(guest_id: int, db: Session = Depends(get_db)):
    return loyalty_service.get_account_by_guest_id(db, guest_id)


@router.post("/{guest_id}/award", response_model=LoyaltyAccountResponse)
def award_points(guest_id: int, request: AwardPointsRequest, db: Session = Depends(get_db)):
    account = loyalty_service.get_account_by_guest_id(db, guest_id)
    return loyalty_service.award_points(db, account.id, request.amount, request.transaction_type, request.description)


@router.post("/{guest_id}/redeem", response_model=LoyaltyAccountResponse)
def redeem_points(guest_id: int, request: RedeemPointsRequest, db: Session = Depends(get_db)):
    account = loyalty_service.get_account_by_guest_id(db, guest_id)
    return loyalty_service.redeem_points(db, account.id, request.amount, request.description)


@router.get("/{guest_id}/transactions", response_model=list[PointsTransactionResponse])
def get_transactions(guest_id: int, limit: int = 50, db: Session = Depends(get_db)):
    account = loyalty_service.get_account_by_guest_id(db, guest_id)
    return loyalty_service.get_transaction_history(db, account.id, limit)
