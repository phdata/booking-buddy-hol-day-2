from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, Enum as SAEnum, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
import enum


class LoyaltyTier(str, enum.Enum):
    Bronze = "Bronze"
    Silver = "Silver"
    Gold = "Gold"


class TransactionType(str, enum.Enum):
    booking_credit = "booking_credit"
    activity_credit = "activity_credit"
    adjustment = "adjustment"
    redemption = "redemption"


class LoyaltyAccount(Base):
    __tablename__ = "loyalty_accounts"

    id = Column(Integer, primary_key=True, index=True)
    guest_id = Column(Integer, unique=True, nullable=False, index=True)
    guest_email = Column(String, nullable=False)
    guest_name = Column(String, nullable=False)
    total_points = Column(Integer, nullable=False, default=0)
    tier = Column(SAEnum(LoyaltyTier), nullable=False, default=LoyaltyTier.Bronze)
    enrolled_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_updated = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    transactions = relationship("PointsTransaction", back_populates="account")


class PointsTransaction(Base):
    __tablename__ = "points_transactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("loyalty_accounts.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    transaction_type = Column(SAEnum(TransactionType), nullable=False)
    description = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    account = relationship("LoyaltyAccount", back_populates="transactions")
