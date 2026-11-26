import uuid

from sqlalchemy import (
    Uuid, String, Text, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class ServiceRequest(TimestampMixin, Base):

    __tablename__ = "service_requests"

    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'in_progress', "
            "'completed', 'cancelled')",
            name="ck_service_request_status"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )

    reservation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("reservations.id"),
        nullable=False,
        index=True
    )

    service_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        server_default="pending",
        nullable=False
    )
