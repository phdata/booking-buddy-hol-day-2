from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from models import PreferredChannel, NotificationType, NotificationStatus


class GuestContactCreate(BaseModel):
    guest_id: int = Field(gt=0)
    email: str = Field(pattern=r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
    phone: str | None = None
    preferred_channel: PreferredChannel = PreferredChannel.email


class GuestContactResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    guest_id: int
    email: str
    phone: str | None
    preferred_channel: PreferredChannel
    opted_in: bool


class SendNotificationRequest(BaseModel):
    guest_id: int = Field(gt=0)
    notification_type: NotificationType
    subject: str = Field(min_length=1, max_length=500)
    body: str = Field(min_length=1, max_length=10000)


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    contact_id: int
    notification_type: NotificationType
    subject: str
    body: str
    channel: PreferredChannel
    status: NotificationStatus
    sent_at: datetime | None
    created_at: datetime
