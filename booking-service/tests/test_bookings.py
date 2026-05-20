def seed_test_data(client):
    from sqlalchemy import text
    from tests.conftest import TestingSessionLocal
    from models import Guest, Itinerary, Cabin, CabinCategory

    db = TestingSessionLocal()
    g = Guest(first_name="Jane", last_name="Smith", email="jane@test.com")
    db.add(g)
    it = Itinerary(name="7-Night Caribbean", destination="Caribbean", duration_nights=7,
                   departure_port="Miami, FL", ship_name="Norwegian Breakaway", base_price_usd=899.0)
    db.add(it)
    c_interior = Cabin(cabin_number="4112", category=CabinCategory.interior, deck=4, max_occupancy=2)
    c_suite = Cabin(cabin_number="10500", category=CabinCategory.suite, deck=10, max_occupancy=2)
    db.add_all([c_interior, c_suite])
    db.commit()
    guest_id = g.id
    itin_id = it.id
    cabin_int_id = c_interior.id
    cabin_suite_id = c_suite.id
    db.close()
    return guest_id, itin_id, cabin_int_id, cabin_suite_id


def test_create_booking_success(client):
    guest_id, itin_id, cabin_id, _ = seed_test_data(client)
    resp = client.post("/bookings/", json={
        "guest_id": guest_id, "itinerary_id": itin_id,
        "cabin_id": cabin_id, "sail_date": "2026-07-01"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "confirmed"
    assert data["total_price_usd"] == 899.0


def test_cabin_price_uplift_suite(client):
    guest_id, itin_id, _, suite_id = seed_test_data(client)
    resp = client.post("/bookings/", json={
        "guest_id": guest_id, "itinerary_id": itin_id,
        "cabin_id": suite_id, "sail_date": "2026-07-01"
    })
    assert resp.status_code == 201
    assert resp.json()["total_price_usd"] == 899.0 + 750.0


def test_double_booking_same_cabin_same_date_rejected(client):
    guest_id, itin_id, cabin_id, _ = seed_test_data(client)
    client.post("/bookings/", json={
        "guest_id": guest_id, "itinerary_id": itin_id,
        "cabin_id": cabin_id, "sail_date": "2026-07-01"
    })
    resp = client.post("/bookings/", json={
        "guest_id": guest_id, "itinerary_id": itin_id,
        "cabin_id": cabin_id, "sail_date": "2026-07-01"
    })
    assert resp.status_code == 409


def test_cancel_booking(client):
    guest_id, itin_id, cabin_id, _ = seed_test_data(client)
    booking = client.post("/bookings/", json={
        "guest_id": guest_id, "itinerary_id": itin_id,
        "cabin_id": cabin_id, "sail_date": "2026-07-01"
    }).json()
    resp = client.delete(f"/bookings/{booking['id']}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "cancelled"


def test_search_itineraries_by_destination(client):
    seed_test_data(client)
    resp = client.get("/itineraries/?destination=Caribbean")
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) >= 1
    assert all("Caribbean" in r["destination"] for r in results)


def test_create_guest_duplicate_email_rejected(client):
    client.post("/guests/", json={"first_name": "Jane", "last_name": "Smith", "email": "jane@test.com"})
    resp = client.post("/guests/", json={"first_name": "Jane", "last_name": "Other", "email": "jane@test.com"})
    assert resp.status_code == 409
