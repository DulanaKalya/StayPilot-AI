import uuid

from datetime import date
from decimal import Decimal

from sqlalchemy import (
    String,
    Integer,
    Uuid,
    Date,
    Numeric,
    ForeignKey,
    CheckConstraint,
    Index
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class Reservation(TimestampMixin, Base):

    __tablename__ = "reservations"

    __table_args__ = (
        CheckConstraint(
            "check_out > check_in",
            name="ck_reservation_dates"
        ),
        CheckConstraint(
            "num_guests > 0",
            name="ck_reservation_guests"
        ),
        CheckConstraint(
            "price_per_night >= 0 AND total_price >= 0",
            name="ck_reservation_prices"
        ),
        CheckConstraint(
            "status IN ('confirmed', 'checked_in', "
            "'checked_out', 'cancelled')",
            name="ck_reservation_status"
        ),
        Index(
            "ix_reservation_room_dates",
            "room_id",
            "check_in",
            "check_out"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid,
        primary_key=True,
        default=uuid.uuid4
    )

    booking_reference: Mapped[str] = mapped_column(
        String(30),
        unique=True,
        nullable=False
    )

    guest_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("guests.id"),
        nullable=False,
        index=True
    )

    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id"),
        nullable=False
    )

    check_in: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    check_out: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    num_guests: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    price_per_night: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    total_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        server_default="confirmed",
        nullable=False
    )
