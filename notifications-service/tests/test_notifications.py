from tests.conftest import TestingSessionLocal
from models import GuestContact, PreferredChannel


def seed_contact(opted_in: bool = True) -> int:
    db = TestingSessionLocal()
    contact = GuestContact(
        guest_id=1,
        email="test@test.com",
        phone="305-555-0000",
        preferred_channel=PreferredChannel.email,
        opted_in=opted_in,
    )
    db.add(contact)
    db.commit()
    guest_id = contact.guest_id
    db.close()
    return guest_id


def test_create_contact(client):
    resp = client.post("/contacts", json={
        "guest_id": 99,
        "email": "new@test.com",
        "preferred_channel": "email"
    })
    assert resp.status_code == 201
    assert resp.json()["guest_id"] == 99


def test_get_contact_not_found(client):
    resp = client.get("/contacts/9999")
    assert resp.status_code == 404


def test_send_notification_success(client):
    guest_id = seed_contact(opted_in=True)
    resp = client.post("/notify", json={
        "guest_id": guest_id,
        "notification_type": "booking_confirmation",
        "subject": "Your booking is confirmed",
        "body": "Dear Guest, your booking is confirmed."
    })
    assert resp.status_code == 201
    assert resp.json()["status"] == "sent"


def test_send_notification_opted_out_suppressed(client):
    guest_id = seed_contact(opted_in=False)
    resp = client.post("/notify", json={
        "guest_id": guest_id,
        "notification_type": "promotional",
        "subject": "Special offer",
        "body": "Book now and save 20%."
    })
    assert resp.status_code == 201
    assert resp.json()["status"] == "suppressed"


def test_notification_history(client):
    guest_id = seed_contact()
    client.post("/notify", json={
        "guest_id": guest_id, "notification_type": "loyalty_update",
        "subject": "Points update", "body": "You earned 500 points."
    })
    client.post("/notify", json={
        "guest_id": guest_id, "notification_type": "booking_confirmation",
        "subject": "Booking confirmed", "body": "Your booking is confirmed."
    })
    resp = client.get(f"/contacts/{guest_id}/history")
    assert resp.status_code == 200
    assert len(resp.json()) == 2
