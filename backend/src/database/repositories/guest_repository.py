from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from src.database.models import Guest, Reservation


class GuestRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, guest_id: UUID):

        return self.db.get(Guest, guest_id)

    def get_by_email(self, email: str):

        stmt = select(Guest).where(
            func.lower(Guest.email) == email.lower()
        )

        return self.db.scalars(stmt).one_or_none()

    def get_by_phone(self, phone: str):

        stmt = select(Guest).where(
            Guest.phone == phone
        )

        return self.db.scalars(stmt).all()

    def create(
        self,
        full_name: str,
        email: str,
        phone: str | None = None
    ):

        guest = Guest(
            full_name=full_name,
            email=email,
            phone=phone
        )

        self.db.add(guest)
        self.db.flush()

        return guest

    def update(self, guest: Guest):

        self.db.flush()

        return guest

    def get_booking_history(self, guest_id: UUID):

        stmt = (
            select(Reservation)
            .where(Reservation.guest_id == guest_id)
            .order_by(Reservation.check_in.desc())
        )

        return self.db.scalars(stmt).all()
