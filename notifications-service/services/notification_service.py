from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from models import GuestContact, Notification, NotificationStatus, PreferredChannel


def get_contact(db: Session, guest_id: int) -> GuestContact:
    contact = db.query(GuestContact).filter(GuestContact.guest_id == guest_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Guest contact not found")
    return contact


def create_or_update_contact(
    db: Session,
    guest_id: int,
    email: str,
    phone: str | None,
    preferred_channel: PreferredChannel,
) -> GuestContact:
    contact = db.query(GuestContact).filter(GuestContact.guest_id == guest_id).first()
    if contact:
        contact.email = email
        contact.phone = phone
        contact.preferred_channel = preferred_channel
    else:
        contact = GuestContact(
            guest_id=guest_id,
            email=email,
            phone=phone,
            preferred_channel=preferred_channel,
        )
        db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


def send_notification(
    db: Session,
    guest_id: int,
    notification_type,
    subject: str,
    body: str,
) -> Notification:
    contact = get_contact(db, guest_id)

    if not contact.opted_in:
        notification = Notification(
            contact_id=contact.id,
            notification_type=notification_type,
            subject=subject,
            body=body,
            channel=contact.preferred_channel,
            status=NotificationStatus.suppressed,
        )
        db.add(notification)
        db.commit()
        db.refresh(notification)
        return notification

    notification = Notification(
        contact_id=contact.id,
        notification_type=notification_type,
        subject=subject,
        body=body,
        channel=contact.preferred_channel,
        status=NotificationStatus.pending,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    return notification


def get_notification_history(db: Session, contact_id: int, limit: int = 20) -> list[Notification]:
    return (
        db.query(Notification)
        .filter(Notification.contact_id == contact_id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
        .all()
    )
