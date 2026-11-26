from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models import Reservation


class ReservationRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, reservation_id: UUID):

        return self.db.get(Reservation, reservation_id)

    def get_by_reference(
        self,
        booking_reference: str,
        guest_id: UUID,
        for_update: bool = False
    ):

        stmt = select(Reservation).where(
            Reservation.booking_reference == booking_reference,
            Reservation.guest_id == guest_id
        )

        if for_update:
            stmt = stmt.with_for_update()

        return self.db.scalars(stmt).one_or_none()

    def get_by_guest(self, guest_id: UUID):

        stmt = (
            select(Reservation)
            .where(Reservation.guest_id == guest_id)
            .order_by(Reservation.check_in.desc())
        )

        return self.db.scalars(stmt).all()

    def create(self, reservation: Reservation):

        self.db.add(reservation)
        self.db.flush()

        return reservation

    def cancel(self, reservation: Reservation):

        reservation.status = "cancelled"

        self.db.flush()

        return reservation
