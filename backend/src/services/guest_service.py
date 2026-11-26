import re

from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database.repositories.guest_repository import (
    GuestRepository
)


class GuestService:

    def __init__(self, db: Session):

        self.db = db
        self.guest_repository = GuestRepository(db)

    @staticmethod
    def normalize_phone(phone: str):

        phone = re.sub(r"[\s\-()]", "", phone)

        if phone.startswith("0"):
            phone = "+94" + phone[1:]

        elif phone.startswith("94"):
            phone = "+" + phone

        if not re.fullmatch(r"\+947\d{8}", phone):
            raise ValueError(
                "Invalid Sri Lankan mobile number."
            )

        return phone

    @staticmethod
    def serialize_guest(guest):

        return {
            "guest_id": str(guest.id),
            "full_name": guest.full_name,
            "email": guest.email,
            "phone": guest.phone,
            "created_at": guest.created_at.isoformat()
        }

    def get_guest_by_id(self, guest_id: UUID):

        guest = self.guest_repository.get_by_id(guest_id)

        if guest is None:
            raise ValueError("Guest not found.")

        return self.serialize_guest(guest)

    def get_guest_by_email(self, email: str):

        guest = self.guest_repository.get_by_email(
            email.strip().lower()
        )

        if guest is None:
            raise ValueError("Guest not found.")

        return self.serialize_guest(guest)

    def get_guest_by_phone(self, phone: str):

        phone = self.normalize_phone(phone)

        guests = self.guest_repository.get_by_phone(phone)

        if not guests:
            raise ValueError("Guest not found.")

        if len(guests) > 1:
            raise ValueError(
                "Multiple guests found. Please use email."
            )

        return self.serialize_guest(guests[0])

    def create_guest(
        self,
        full_name: str,
        email: str,
        phone: str | None = None
    ):

        full_name = full_name.strip()
        email = email.strip().lower()

        if not full_name or len(full_name) > 150:
            raise ValueError("Invalid guest name.")

        if (
            len(email) > 255
            or not re.fullmatch(
                r"[^@\s]+@[^@\s]+\.[^@\s]+", email
            )
        ):
            raise ValueError("Invalid email address.")

        if phone is not None:
            phone = self.normalize_phone(phone)

        existing_guest = (
            self.guest_repository.get_by_email(email)
        )

        if existing_guest is not None:
            raise ValueError(
                "A guest with this email already exists."
            )

        try:

            guest = self.guest_repository.create(
                full_name=full_name,
                email=email,
                phone=phone
            )

            self.db.commit()
            self.db.refresh(guest)

            return self.serialize_guest(guest)

        except IntegrityError as error:

            self.db.rollback()

            raise ValueError(
                "Guest registration conflicts with existing data."
            ) from error

    def update_guest(
        self,
        guest_id: UUID,
        full_name: str | None = None,
        phone: str | None = None
    ):

        guest = self.guest_repository.get_by_id(guest_id)

        if guest is None:
            raise ValueError("Guest not found.")

        if full_name is not None:
            full_name = full_name.strip()

            if not full_name or len(full_name) > 150:
                raise ValueError("Invalid guest name.")

        if phone is not None:
            phone = self.normalize_phone(phone)

        if full_name is not None:
            guest.full_name = full_name

        if phone is not None:
            guest.phone = phone

        try:

            self.guest_repository.update(guest)

            self.db.commit()
            self.db.refresh(guest)

            return self.serialize_guest(guest)

        except IntegrityError as error:

            self.db.rollback()

            raise ValueError(
                "Unable to update guest information."
            ) from error

    def get_booking_history(self, guest_id: UUID):

        guest = self.guest_repository.get_by_id(guest_id)

        if guest is None:
            raise ValueError("Guest not found.")

        reservations = (
            self.guest_repository.get_booking_history(
                guest_id
            )
        )

        return {
            "guest_id": str(guest.id),
            "full_name": guest.full_name,
            "total_reservations": len(reservations),
            "reservations": [
                {
                    "reservation_id": str(reservation.id),
                    "booking_reference": reservation.booking_reference,
                    "room_id": reservation.room_id,
                    "check_in": reservation.check_in.isoformat(),
                    "check_out": reservation.check_out.isoformat(),
                    "total_price": str(reservation.total_price),
                    "currency": "USD",
                    "status": reservation.status
                }
                for reservation in reservations
            ]
        }
