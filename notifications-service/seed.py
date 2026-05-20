from database import SessionLocal, init_db
from models import GuestContact, Notification, PreferredChannel, NotificationType, NotificationStatus
from datetime import datetime

init_db()
db = SessionLocal()

contacts = [
    GuestContact(guest_id=1, email="margaret.thornton@email.com", phone="305-555-0142", preferred_channel=PreferredChannel.email, opted_in=True),
    GuestContact(guest_id=2, email="creyes@email.com", phone="786-555-0281", preferred_channel=PreferredChannel.sms, opted_in=True),
    GuestContact(guest_id=3, email="pkim@email.com", phone="212-555-0394", preferred_channel=PreferredChannel.email, opted_in=True),
    GuestContact(guest_id=4, email="jokafor@email.com", phone="415-555-0517", preferred_channel=PreferredChannel.push, opted_in=True),
    GuestContact(guest_id=5, email="snakamura@email.com", phone="617-555-0638", preferred_channel=PreferredChannel.email, opted_in=False),
    GuestContact(guest_id=6, email="rvasquez@email.com", phone="713-555-0751", preferred_channel=PreferredChannel.sms, opted_in=True),
    GuestContact(guest_id=7, email="lchen@email.com", phone="206-555-0864", preferred_channel=PreferredChannel.email, opted_in=True),
    GuestContact(guest_id=8, email="wosei@email.com", phone="404-555-0977", preferred_channel=PreferredChannel.email, opted_in=True),
]
db.add_all(contacts)
db.flush()

notifications = [
    Notification(contact_id=1, notification_type=NotificationType.booking_confirmation, subject="Your booking is confirmed — 7-Night Eastern Caribbean", body="Dear Margaret, your booking for the 7-Night Eastern Caribbean sailing on June 14, 2026 is confirmed.", channel=PreferredChannel.email, status=NotificationStatus.sent, sent_at=datetime(2026, 3, 15, 10, 22)),
    Notification(contact_id=2, notification_type=NotificationType.booking_confirmation, subject="Booking confirmed — 10-Night Mediterranean Majesty", body="Dear Carlos, your booking for the Mediterranean sailing on July 5, 2026 is confirmed.", channel=PreferredChannel.sms, status=NotificationStatus.sent, sent_at=datetime(2026, 3, 20, 14, 5)),
    Notification(contact_id=3, notification_type=NotificationType.loyalty_update, subject="You've reached Silver status!", body="Congratulations Patricia — you now have 1,000 Latitudes points and have achieved Silver tier.", channel=PreferredChannel.email, status=NotificationStatus.sent, sent_at=datetime(2026, 4, 1, 9, 0)),
    Notification(contact_id=4, notification_type=NotificationType.booking_confirmation, subject="Booking confirmed — 7-Night Western Caribbean", body="Dear James, your booking for the Western Caribbean sailing on June 21, 2026 is confirmed.", channel=PreferredChannel.push, status=NotificationStatus.sent, sent_at=datetime(2026, 3, 18, 11, 30)),
    Notification(contact_id=5, notification_type=NotificationType.loyalty_update, subject="Points update", body="Susan, your points balance has been updated.", channel=PreferredChannel.email, status=NotificationStatus.suppressed, sent_at=None),
    Notification(contact_id=6, notification_type=NotificationType.loyalty_update, subject="Approaching Gold status — 5,000 points!", body="Robert, you've reached 5,000 Latitudes points. Gold status is within reach.", channel=PreferredChannel.sms, status=NotificationStatus.sent, sent_at=datetime(2026, 4, 10, 8, 15)),
    Notification(contact_id=7, notification_type=NotificationType.loyalty_update, subject="Gold status achieved!", body="Congratulations Linda — welcome to Gold tier! Enjoy priority boarding and exclusive benefits.", channel=PreferredChannel.email, status=NotificationStatus.sent, sent_at=datetime(2026, 4, 11, 9, 0)),
    Notification(contact_id=1, notification_type=NotificationType.itinerary_update, subject="Important update: Port of call change", body="Dear Margaret, due to weather, Grand Cayman has been replaced with Cozumel on your June 14 sailing.", channel=PreferredChannel.email, status=NotificationStatus.sent, sent_at=datetime(2026, 6, 1, 7, 0)),
]
db.add_all(notifications)

db.commit()
db.close()
print("Notifications service seeded.")
