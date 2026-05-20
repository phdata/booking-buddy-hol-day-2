from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import relationship
from database import Base
import enum


class PreferredChannel(str, enum.Enum):
    email = "email"
    sms = "sms"
    push = "push"


class NotificationType(str, enum.Enum):
    booking_confirmation = "booking_confirmation"
    itinerary_update = "itinerary_update"
    loyalty_update = "loyalty_update"
    promotional = "promotional"


class NotificationStatus(str, enum.Enum):
    pending = "pending"
    sent = "sent"
    failed = "failed"
    suppressed = "suppressed"


class GuestContact(Base):
    __tablename__ = "guest_contacts"

    id = Column(Integer, primary_key=True, index=True)
    guest_id = Column(Integer, unique=True, nullable=False, index=True)
    email = Column(String, nullable=False)
    phone = Column(String)
    preferred_channel = Column(SAEnum(PreferredChannel), nullable=False, default=PreferredChannel.email)
    opted_in = Column(Boolean, nullable=False, default=True)

    notifications = relationship("Notification", back_populates="contact")


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    contact_id = Column(Integer, ForeignKey("guest_contacts.id"), nullable=False)
    notification_type = Column(SAEnum(NotificationType), nullable=False)
    subject = Column(String, nullable=False)
    body = Column(String, nullable=False)
    channel = Column(SAEnum(PreferredChannel), nullable=False)
    status = Column(SAEnum(NotificationStatus), nullable=False, default=NotificationStatus.pending)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    contact = relationship("GuestContact", back_populates="notifications")
