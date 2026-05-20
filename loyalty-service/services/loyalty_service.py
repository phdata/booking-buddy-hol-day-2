from datetime import datetime, timezone
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import LoyaltyAccount, LoyaltyTier, PointsTransaction, TransactionType


def calculate_tier(points: int) -> LoyaltyTier:
    """Determine loyalty tier based on total points."""
    if points > 5000:
        return LoyaltyTier.Gold
    elif points >= 1000:
        return LoyaltyTier.Silver
    else:
        return LoyaltyTier.Bronze


def get_account_by_guest_id(db: Session, guest_id: int) -> LoyaltyAccount:
    account = db.query(LoyaltyAccount).filter(LoyaltyAccount.guest_id == guest_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Loyalty account not found")
    return account


def award_points(
    db: Session,
    account_id: int,
    amount: int,
    transaction_type: TransactionType,
    description: str,
) -> LoyaltyAccount:
    account = db.query(LoyaltyAccount).filter(LoyaltyAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Loyalty account not found")

    transaction = PointsTransaction(
        account_id=account_id,
        amount=amount,
        transaction_type=transaction_type,
        description=description,
    )
    db.add(transaction)

    account.total_points += amount
    account.tier = calculate_tier(account.total_points)
    account.last_updated = datetime.now(timezone.utc)
    db.commit()
    db.refresh(account)
    return account


def redeem_points(db: Session, account_id: int, amount: int, description: str) -> LoyaltyAccount:
    account = db.query(LoyaltyAccount).filter(LoyaltyAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Loyalty account not found")

    if account.total_points < amount:
        raise HTTPException(status_code=400, detail="Insufficient points balance")

    transaction = PointsTransaction(
        account_id=account_id,
        amount=-amount,
        transaction_type=TransactionType.redemption,
        description=description,
    )
    db.add(transaction)

    account.total_points -= amount
    account.tier = calculate_tier(account.total_points)
    account.last_updated = datetime.now(timezone.utc)
    db.commit()
    db.refresh(account)
    return account


def get_transaction_history(db: Session, account_id: int, limit: int = 50) -> list[PointsTransaction]:
    return (
        db.query(PointsTransaction)
        .filter(PointsTransaction.account_id == account_id)
        .order_by(PointsTransaction.created_at.desc())
        .limit(limit)
        .all()
    )
