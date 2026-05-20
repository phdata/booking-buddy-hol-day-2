from database import SessionLocal, init_db
from models import Ship, Cabin, Sailing, ShipClass, ShipStatus, CabinCategory

init_db()
db = SessionLocal()

ships = [
    Ship(name="Norwegian Breakaway", imo_number="9548898", class_name=ShipClass.breakaway, total_cabins=1836, passenger_capacity=3963, home_port="New York, NY", status=ShipStatus.active),
    Ship(name="Norwegian Joy", imo_number="9721000", class_name=ShipClass.joy, total_cabins=1716, passenger_capacity=3804, home_port="Los Angeles, CA", status=ShipStatus.active),
    Ship(name="Norwegian Bliss", imo_number="9751509", class_name=ShipClass.bliss, total_cabins=1716, passenger_capacity=3998, home_port="Seattle, WA", status=ShipStatus.active),
    Ship(name="Norwegian Encore", imo_number="9793316", class_name=ShipClass.encore, total_cabins=1735, passenger_capacity=3998, home_port="Miami, FL", status=ShipStatus.active),
]
db.add_all(ships)
db.flush()

cabins = []
for ship in ships:
    cabins += [
        Cabin(ship_id=ship.id, cabin_number="4101", category=CabinCategory.interior, deck=4, max_occupancy=2, base_rate_usd=129.0),
        Cabin(ship_id=ship.id, cabin_number="4103", category=CabinCategory.interior, deck=4, max_occupancy=2, base_rate_usd=129.0),
        Cabin(ship_id=ship.id, cabin_number="4105", category=CabinCategory.interior, deck=4, max_occupancy=3, base_rate_usd=139.0),
        Cabin(ship_id=ship.id, cabin_number="4107", category=CabinCategory.interior, deck=4, max_occupancy=4, base_rate_usd=149.0),
        Cabin(ship_id=ship.id, cabin_number="6201", category=CabinCategory.ocean_view, deck=6, max_occupancy=2, base_rate_usd=179.0),
        Cabin(ship_id=ship.id, cabin_number="6203", category=CabinCategory.ocean_view, deck=6, max_occupancy=2, base_rate_usd=179.0),
        Cabin(ship_id=ship.id, cabin_number="6205", category=CabinCategory.ocean_view, deck=6, max_occupancy=4, base_rate_usd=199.0),
        Cabin(ship_id=ship.id, cabin_number="8301", category=CabinCategory.balcony, deck=8, max_occupancy=2, base_rate_usd=249.0),
        Cabin(ship_id=ship.id, cabin_number="8303", category=CabinCategory.balcony, deck=8, max_occupancy=2, base_rate_usd=249.0),
        Cabin(ship_id=ship.id, cabin_number="8305", category=CabinCategory.balcony, deck=8, max_occupancy=3, base_rate_usd=269.0),
        Cabin(ship_id=ship.id, cabin_number="10501", category=CabinCategory.suite, deck=10, max_occupancy=2, base_rate_usd=549.0),
        Cabin(ship_id=ship.id, cabin_number="10503", category=CabinCategory.suite, deck=10, max_occupancy=4, base_rate_usd=649.0),
    ]
db.add_all(cabins)

sailings = [
    Sailing(ship_id=1, departure_date="2026-06-14", arrival_date="2026-06-21", departure_port="New York, NY", arrival_port="New York, NY", itinerary_name="7-Night Bermuda Round Trip"),
    Sailing(ship_id=1, departure_date="2026-07-12", arrival_date="2026-07-26", departure_port="New York, NY", arrival_port="Southampton, UK", itinerary_name="14-Night Transatlantic Crossing"),
    Sailing(ship_id=2, departure_date="2026-06-21", arrival_date="2026-06-28", departure_port="Los Angeles, CA", arrival_port="Los Angeles, CA", itinerary_name="7-Night Mexican Riviera"),
    Sailing(ship_id=2, departure_date="2026-08-02", arrival_date="2026-08-09", departure_port="Los Angeles, CA", arrival_port="Los Angeles, CA", itinerary_name="7-Night Pacific Coast"),
    Sailing(ship_id=3, departure_date="2026-05-31", arrival_date="2026-06-07", departure_port="Seattle, WA", arrival_port="Vancouver, BC", itinerary_name="7-Night Alaska Inside Passage"),
    Sailing(ship_id=3, departure_date="2026-07-19", arrival_date="2026-07-26", departure_port="Seattle, WA", arrival_port="Vancouver, BC", itinerary_name="7-Night Alaska Glacier Bay"),
    Sailing(ship_id=4, departure_date="2026-06-28", arrival_date="2026-07-05", departure_port="Miami, FL", arrival_port="Miami, FL", itinerary_name="7-Night Eastern Caribbean"),
    Sailing(ship_id=4, departure_date="2026-08-16", arrival_date="2026-08-26", departure_port="Barcelona, Spain", arrival_port="Rome, Italy", itinerary_name="10-Night Mediterranean Highlights"),
]
db.add_all(sailings)

db.commit()
db.close()
print("Fleet service seeded.")
