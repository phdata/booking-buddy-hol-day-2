from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from database import get_db
from models import GuestContact
from schemas import GuestContactCreate, GuestContactResponse, SendNotificationRequest, NotificationResponse
from services import notification_service

router = APIRouter()


@router.post("/contacts", response_model=GuestContactResponse)
def create_contact(contact: GuestContactCreate, response: Response, db: Session = Depends(get_db)):
    is_new = db.query(GuestContact).filter(GuestContact.guest_id == contact.guest_id).first() is None
    result = notification_service.create_or_update_contact(
        db, contact.guest_id, contact.email, contact.phone, contact.preferred_channel
    )
    response.status_code = 201 if is_new else 200
    return result


@router.get("/contacts/{guest_id}", response_model=GuestContactResponse)
def get_contact(guest_id: int, db: Session = Depends(get_db)):
    return notification_service.get_contact(db, guest_id)


@router.get("/contacts/{guest_id}/history", response_model=list[NotificationResponse])
def get_notification_history(guest_id: int, limit: int = Query(20, ge=1, le=500), db: Session = Depends(get_db)):
    contact = notification_service.get_contact(db, guest_id)
    return notification_service.get_notification_history(db, contact.id, limit)


@router.post("/notify", response_model=NotificationResponse, status_code=201)
def send_notification(request: SendNotificationRequest, db: Session = Depends(get_db)):
    return notification_service.send_notification(
        db, request.guest_id, request.notification_type, request.subject, request.body
    )
