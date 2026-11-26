from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from src.database.repositories.room_repository import (
    RoomRepository
)


class ReservationService:

    def __init__(self, db: Session):

        self.db = db
        self.room_repository = RoomRepository(db)

    def check_availability(
        self,
        check_in: date,
        check_out: date,
        num_guests: int,
        room_type: str | None = None
    ):

        today = datetime.now(
            ZoneInfo("Asia/Colombo")
        ).date()

        if check_in < today:
            raise ValueError(
                "Check-in date cannot be in the past."
            )

        if check_out <= check_in:
            raise ValueError(
                "Check-out must be after check-in."
            )

        if num_guests <= 0:
            raise ValueError(
                "Number of guests must be positive."
            )

        available_rooms = (
            self.room_repository.get_available_rooms(
                check_in=check_in,
                check_out=check_out,
                num_guests=num_guests,
                room_type=room_type
            )
        )

        nights = (check_out - check_in).days

        grouped_rooms = {}

        for room, category in available_rooms:

            if category.id not in grouped_rooms:

                grouped_rooms[category.id] = {
                    "room_type_id": category.id,
                    "room_type": category.name,
                    "description": category.description,
                    "price_per_night": category.price_per_night,
                    "total_price": (
                        category.price_per_night * nights
                    ),
                    "currency": "USD",
                    "max_guests": category.max_guests,
                    "amenities": category.amenities,
                    "available_rooms": 0
                }

            grouped_rooms[category.id]["available_rooms"] += 1

        return {
            "check_in": check_in.isoformat(),
            "check_out": check_out.isoformat(),
            "num_guests": num_guests,
            "nights": nights,
            "available": bool(grouped_rooms),
            "options": list(grouped_rooms.values())
        }
