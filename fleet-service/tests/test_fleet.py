from tests.conftest import TestingSessionLocal
from models import Ship, Cabin, Sailing, ShipClass, ShipStatus, CabinCategory


def seed_ship_with_cabins(num_cabins: int = 12) -> int:
    db = TestingSessionLocal()
    ship = Ship(
        name="Norwegian Breakaway",
        imo_number="9548898",
        class_name=ShipClass.breakaway,
        total_cabins=1836,
        passenger_capacity=3963,
        home_port="New York, NY",
        status=ShipStatus.active,
    )
    db.add(ship)
    db.flush()

    categories = [CabinCategory.interior, CabinCategory.ocean_view, CabinCategory.balcony, CabinCategory.suite]
    for i in range(num_cabins):
        db.add(Cabin(
            ship_id=ship.id,
            cabin_number=f"{4000 + i}",
            category=categories[i % 4],
            deck=4 + (i // 4),
            max_occupancy=2,
            base_rate_usd=129.0 + (i % 4) * 50,
        ))

    ship_id = ship.id
    db.commit()
    db.close()
    return ship_id


def test_list_ships(client):
    seed_ship_with_cabins()
    resp = client.get("/ships/")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_list_ships_active_only(client):
    seed_ship_with_cabins()
    resp = client.get("/ships/?status=active")
    assert resp.status_code == 200
    assert all(s["status"] == "active" for s in resp.json())


def test_get_ship_not_found(client):
    resp = client.get("/ships/9999")
    assert resp.status_code == 404


def test_cabin_categories_exist(client):
    ship_id = seed_ship_with_cabins(12)
    resp = client.get(f"/ships/{ship_id}/cabins")
    assert resp.status_code == 200
    categories = {c["category"] for c in resp.json()}
    assert categories == {"interior", "ocean_view", "balcony", "suite"}


def test_available_cabins_respects_limit(client):
    """Requesting limit=3 should return at most 3 cabins."""
    ship_id = seed_ship_with_cabins(12)
    resp = client.get(f"/ships/{ship_id}/cabins/available?limit=3")
    assert resp.status_code == 200
    # limit=3 must be respected regardless of total cabins seeded
    assert len(resp.json()) <= 3


def test_list_sailings(client):
    db = TestingSessionLocal()
    ship = Ship(name="Norwegian Joy", imo_number="9721000", class_name=ShipClass.joy,
                total_cabins=1716, passenger_capacity=3804, home_port="Los Angeles, CA", status=ShipStatus.active)
    db.add(ship)
    db.flush()
    db.add(Sailing(ship_id=ship.id, departure_date="2026-07-01", arrival_date="2026-07-08",
                   departure_port="Los Angeles, CA", arrival_port="Los Angeles, CA",
                   itinerary_name="7-Night Mexican Riviera"))
    db.commit()
    db.close()

    resp = client.get("/sailings/")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
