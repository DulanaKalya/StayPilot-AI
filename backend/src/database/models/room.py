from sqlalchemy import (
    Integer, String, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Room(Base):

    __tablename__ = "rooms"

    __table_args__ = (
        CheckConstraint(
            "status IN ('active', 'maintenance', 'inactive')",
            name="ck_room_status"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    room_number: Mapped[str] = mapped_column(
        String(10),
        unique=True,
        nullable=False
    )

    room_type_id: Mapped[int] = mapped_column(
        ForeignKey("room_types.id"),
        nullable=False,
        index=True
    )

    floor: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        server_default="active",
        nullable=False
    )
