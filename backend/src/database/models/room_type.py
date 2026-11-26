from decimal import Decimal

from sqlalchemy import (
    String, Integer, Text, Numeric, CheckConstraint, text
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class RoomType(Base):

    __tablename__ = "room_types"

    __table_args__ = (
        CheckConstraint(
            "price_per_night >= 0",
            name="ck_room_type_price"
        ),
        CheckConstraint(
            "max_guests > 0",
            name="ck_room_type_capacity"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    price_per_night: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False
    )

    max_guests: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    amenities: Mapped[list] = mapped_column(
        JSONB,
        default=list,
        server_default=text("'[]'::jsonb"),
        nullable=False
    )
