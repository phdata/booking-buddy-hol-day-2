from tests.conftest import TestingSessionLocal
from models import LoyaltyAccount, LoyaltyTier


def seed_account(points: int, tier: LoyaltyTier = LoyaltyTier.Bronze) -> int:
    db = TestingSessionLocal()
    account = LoyaltyAccount(
        guest_id=1,
        guest_email="test@test.com",
        guest_name="Test Guest",
        total_points=points,
        tier=tier,
    )
    db.add(account)
    db.commit()
    guest_id = account.guest_id
    db.close()
    return guest_id


def test_get_account(client):
    guest_id = seed_account(500)
    resp = client.get(f"/accounts/{guest_id}")
    assert resp.status_code == 200
    assert resp.json()["total_points"] == 500
    assert resp.json()["tier"] == "Bronze"


def test_silver_threshold(client):
    guest_id = seed_account(1000, LoyaltyTier.Silver)
    resp = client.post(f"/accounts/{guest_id}/award", json={"amount": 0, "description": "test", "transaction_type": "adjustment"})
    # Award 0 points — recalculates tier — 1000 should stay Silver
    assert resp.status_code == 200
    assert resp.json()["tier"] == "Silver"


def test_gold_threshold_above(client):
    guest_id = seed_account(5001, LoyaltyTier.Gold)
    resp = client.get(f"/accounts/{guest_id}")
    assert resp.status_code == 200
    # 5001 is > 5000, so even buggy code returns Gold
    assert resp.json()["tier"] == "Gold"


def test_gold_threshold_exact(client):
    """A guest with exactly 5000 points should be Gold tier."""
    guest_id = seed_account(4999, LoyaltyTier.Silver)
    # Award 1 point to push to exactly 5000
    resp = client.post(f"/accounts/{guest_id}/award", json={
        "amount": 1,
        "transaction_type": "booking_credit",
        "description": "Final qualifying point"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_points"] == 5000
    assert data["tier"] == "Gold"  # a guest at exactly the Gold threshold should be Gold


def test_award_points_updates_tier(client):
    guest_id = seed_account(900, LoyaltyTier.Bronze)
    resp = client.post(f"/accounts/{guest_id}/award", json={
        "amount": 200,
        "transaction_type": "booking_credit",
        "description": "Caribbean sailing credit"
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_points"] == 1100
    assert data["tier"] == "Silver"


def test_redeem_insufficient_balance(client):
    guest_id = seed_account(200)
    resp = client.post(f"/accounts/{guest_id}/redeem", json={
        "amount": 500,
        "description": "Onboard credit"
    })
    assert resp.status_code == 400


def test_redeem_points_success(client):
    guest_id = seed_account(2000, LoyaltyTier.Silver)
    resp = client.post(f"/accounts/{guest_id}/redeem", json={
        "amount": 500,
        "description": "Onboard credit"
    })
    assert resp.status_code == 200
    assert resp.json()["total_points"] == 1500
