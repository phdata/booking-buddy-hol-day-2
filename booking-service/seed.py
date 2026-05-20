from database import SessionLocal, init_db
from models import Guest, Itinerary, Cabin, Booking, CabinCategory, BookingStatus

init_db()
db = SessionLocal()

guests = [
    Guest(first_name="Margaret", last_name="Thornton", email="margaret.thornton@email.com", phone="305-555-0142"),
    Guest(first_name="Carlos", last_name="Reyes", email="creyes@email.com", phone="786-555-0281"),
    Guest(first_name="Patricia", last_name="Kim", email="pkim@email.com", phone="212-555-0394"),
    Guest(first_name="James", last_name="Okafor", email="jokafor@email.com", phone="415-555-0517"),
    Guest(first_name="Susan", last_name="Nakamura", email="snakamura@email.com", phone="617-555-0638"),
    Guest(first_name="Robert", last_name="Vasquez", email="rvasquez@email.com", phone="713-555-0751"),
    Guest(first_name="Linda", last_name="Chen", email="lchen@email.com", phone="206-555-0864"),
    Guest(first_name="William", last_name="Osei", email="wosei@email.com", phone="404-555-0977"),
]
db.add_all(guests)

itineraries = [
    Itinerary(name="7-Night Eastern Caribbean", destination="Caribbean", duration_nights=7, departure_port="Miami, FL", ship_name="Norwegian Breakaway", base_price_usd=899.0),
    Itinerary(name="7-Night Western Caribbean", destination="Caribbean", duration_nights=7, departure_port="New Orleans, LA", ship_name="Norwegian Joy", base_price_usd=849.0),
    Itinerary(name="10-Night Mediterranean Majesty", destination="Mediterranean", duration_nights=10, departure_port="Barcelona, Spain", ship_name="Norwegian Encore", base_price_usd=1499.0),
    Itinerary(name="7-Night Alaska Inside Passage", destination="Alaska", duration_nights=7, departure_port="Seattle, WA", ship_name="Norwegian Bliss", base_price_usd=1199.0),
    Itinerary(name="14-Night Transatlantic Crossing", destination="Transatlantic", duration_nights=14, departure_port="New York, NY", ship_name="Norwegian Breakaway", base_price_usd=1899.0),
]
db.add_all(itineraries)

cabins = [
    Cabin(cabin_number="4112", category=CabinCategory.interior, deck=4, max_occupancy=2),
    Cabin(cabin_number="4114", category=CabinCategory.interior, deck=4, max_occupancy=2),
    Cabin(cabin_number="4116", category=CabinCategory.interior, deck=4, max_occupancy=3),
    Cabin(cabin_number="6220", category=CabinCategory.ocean_view, deck=6, max_occupancy=2),
    Cabin(cabin_number="6222", category=CabinCategory.ocean_view, deck=6, max_occupancy=2),
    Cabin(cabin_number="6224", category=CabinCategory.ocean_view, deck=6, max_occupancy=4),
    Cabin(cabin_number="8310", category=CabinCategory.balcony, deck=8, max_occupancy=2),
    Cabin(cabin_number="8312", category=CabinCategory.balcony, deck=8, max_occupancy=2),
    Cabin(cabin_number="8314", category=CabinCategory.balcony, deck=8, max_occupancy=3),
    Cabin(cabin_number="10500", category=CabinCategory.suite, deck=10, max_occupancy=2),
    Cabin(cabin_number="10502", category=CabinCategory.suite, deck=10, max_occupancy=4),
    Cabin(cabin_number="10504", category=CabinCategory.suite, deck=10, max_occupancy=2),
]
db.add_all(cabins)
db.flush()

bookings = [
    Booking(guest_id=1, itinerary_id=1, cabin_id=7, sail_date="2026-06-14", status=BookingStatus.confirmed, total_price_usd=1199.0),
    Booking(guest_id=2, itinerary_id=3, cabin_id=10, sail_date="2026-07-05", status=BookingStatus.confirmed, total_price_usd=2249.0),
    Booking(guest_id=3, itinerary_id=4, cabin_id=4, sail_date="2026-08-09", status=BookingStatus.confirmed, total_price_usd=1349.0),
    Booking(guest_id=4, itinerary_id=2, cabin_id=1, sail_date="2026-06-21", status=BookingStatus.confirmed, total_price_usd=849.0),
    Booking(guest_id=5, itinerary_id=5, cabin_id=11, sail_date="2026-09-12", status=BookingStatus.confirmed, total_price_usd=2649.0),
    Booking(guest_id=1, itinerary_id=2, cabin_id=3, sail_date="2025-11-08", status=BookingStatus.cancelled, total_price_usd=849.0),
]
db.add_all(bookings)

db.commit()
db.close()
print("Booking service seeded.")
