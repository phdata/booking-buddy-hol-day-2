from database import SessionLocal, init_db
from models import LoyaltyAccount, PointsTransaction, LoyaltyTier, TransactionType

init_db()
db = SessionLocal()

accounts = [
    LoyaltyAccount(guest_id=1, guest_email="margaret.thornton@email.com", guest_name="Margaret Thornton", total_points=750, tier=LoyaltyTier.Bronze),
    LoyaltyAccount(guest_id=2, guest_email="creyes@email.com", guest_name="Carlos Reyes", total_points=999, tier=LoyaltyTier.Bronze),
    LoyaltyAccount(guest_id=3, guest_email="pkim@email.com", guest_name="Patricia Kim", total_points=1000, tier=LoyaltyTier.Silver),
    LoyaltyAccount(guest_id=4, guest_email="jokafor@email.com", guest_name="James Okafor", total_points=2450, tier=LoyaltyTier.Silver),
    LoyaltyAccount(guest_id=5, guest_email="snakamura@email.com", guest_name="Susan Nakamura", total_points=4999, tier=LoyaltyTier.Silver),
    LoyaltyAccount(guest_id=6, guest_email="rvasquez@email.com", guest_name="Robert Vasquez", total_points=5000, tier=LoyaltyTier.Gold),
    LoyaltyAccount(guest_id=7, guest_email="lchen@email.com", guest_name="Linda Chen", total_points=5001, tier=LoyaltyTier.Gold),
    LoyaltyAccount(guest_id=8, guest_email="wosei@email.com", guest_name="William Osei", total_points=12500, tier=LoyaltyTier.Gold),
]
db.add_all(accounts)
db.flush()

transactions = [
    PointsTransaction(account_id=1, amount=750, transaction_type=TransactionType.booking_credit, description="7-Night Eastern Caribbean sailing Jun 2026"),
    PointsTransaction(account_id=2, amount=849, transaction_type=TransactionType.booking_credit, description="7-Night Western Caribbean sailing Nov 2025"),
    PointsTransaction(account_id=2, amount=150, transaction_type=TransactionType.redemption, description="Onboard credit redemption"),
    PointsTransaction(account_id=3, amount=1000, transaction_type=TransactionType.booking_credit, description="10-Night Mediterranean sailing Jul 2026"),
    PointsTransaction(account_id=4, amount=2450, transaction_type=TransactionType.booking_credit, description="Multiple sailings credit"),
    PointsTransaction(account_id=5, amount=4999, transaction_type=TransactionType.booking_credit, description="Platinum tier qualifying spend"),
    PointsTransaction(account_id=6, amount=5000, transaction_type=TransactionType.booking_credit, description="Gold tier qualifying booking"),
    PointsTransaction(account_id=7, amount=5001, transaction_type=TransactionType.booking_credit, description="Gold tier qualifying booking"),
    PointsTransaction(account_id=8, amount=12500, transaction_type=TransactionType.booking_credit, description="Multi-year sailing history"),
]
db.add_all(transactions)

db.commit()
db.close()
print("Loyalty service seeded.")
