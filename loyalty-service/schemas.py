from datetime import datetime
from pydantic import BaseModel, ConfigDict
from models import LoyaltyTier, TransactionType


class LoyaltyAccountResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guest_id: int
    guest_email: str
    guest_name: str
    total_points: int
    tier: LoyaltyTier
    enrolled_at: datetime
    last_updated: datetime


class PointsTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    amount: int
    transaction_type: TransactionType
    description: str
    created_at: datetime


class AwardPointsRequest(BaseModel):
    amount: int
    transaction_type: TransactionType = TransactionType.booking_credit
    description: str


class RedeemPointsRequest(BaseModel):
    amount: int
    description: str
