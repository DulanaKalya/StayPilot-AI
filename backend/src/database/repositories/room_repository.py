from datetime import date

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.database.models import Room, RoomType, Reservation


class RoomRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_all_room_types(self):

        stmt = select(RoomType).order_by(
            RoomType.price_per_night
        )

        return self.db.scalars(stmt).all()

    def get_room_type_by_id(self, room_type_id: int):

        return self.db.get(RoomType, room_type_id)

    def get_room_by_id(self, room_id: int):

        return self.db.get(Room, room_id)

    def get_available_rooms(
        self,
        check_in: date,
        check_out: date,
        num_guests: int,
        room_type: str | None = None
    ):

        overlapping_reservation = (
            select(Reservation.id)
            .where(
                Reservation.room_id == Room.id,
                Reservation.status.in_([
                    "confirmed",
                    "checked_in"
                ]),
                Reservation.check_in < check_out,
                Reservation.check_out > check_in
            )
            .exists()
        )

        stmt = (
            select(Room, RoomType)
            .join(
                RoomType,
                Room.room_type_id == RoomType.id
            )
            .where(
                Room.status == "active",
                RoomType.max_guests >= num_guests,
                ~overlapping_reservation
            )
        )

        if room_type is not None:

            stmt = stmt.where(
                func.lower(RoomType.name)
                == room_type.strip().lower()
            )

        stmt = stmt.order_by(
            RoomType.price_per_night,
            Room.room_number
        )

        return self.db.execute(stmt).all()
