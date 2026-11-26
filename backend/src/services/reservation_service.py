from datetime import date, datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session

from src.database.repositories.room_repository import (
    RoomRepository
)

from uuid import UUID
from decimal import Decimal
from base64 import b32encode

from sqlalchemy.exc import IntegrityError

from src.database.models import Reservation

from src.database.repositories.guest_repository import (
    GuestRepository
)

from src.database.repositories.reservation_repository import (
    ReservationRepository
)


class ReservationService:

    def __init__(self, db: Session):

        self.db = db

        self.room_repository = RoomRepository(db)

        self.guest_repository = GuestRepository(db)

        self.reservation_repository = ReservationRepository(db)

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

    @staticmethod
    def generate_booking_reference(request_id: UUID):

        encoded = b32encode(request_id.bytes).decode().rstrip("=")

        return f"SP-{encoded}"

    @staticmethod
    def serialize_reservation(reservation):

        return {
            "reservation_id": str(reservation.id),
            "booking_reference": reservation.booking_reference,
            "guest_id": str(reservation.guest_id),
            "room_id": reservation.room_id,
            "check_in": reservation.check_in.isoformat(),
            "check_out": reservation.check_out.isoformat(),
            "num_guests": reservation.num_guests,
            "nights": (
                    reservation.check_out - reservation.check_in
            ).days,
            "price_per_night": str(reservation.price_per_night),
            "total_price": str(reservation.total_price),
            "currency": "USD",
            "status": reservation.status,
            "created_at": reservation.created_at.isoformat()
        }

    def _check_existing_request(
        self,
        request_id: UUID,
        guest_id: UUID,
        room_type_id: int,
        check_in: date,
        check_out: date,
        num_guests: int,
        expected_total_price: Decimal
    ):

        existing = self.reservation_repository.get_by_id(
            request_id
        )

        if existing is None:
            return None

        room = self.room_repository.get_room_by_id(
            existing.room_id
        )

        if (
            existing.guest_id != guest_id
            or room is None
            or room.room_type_id != room_type_id
            or existing.check_in != check_in
            or existing.check_out != check_out
            or existing.num_guests != num_guests
            or existing.total_price != expected_total_price
        ):
            raise ValueError(
                "Request ID conflicts with an existing booking."
            )

        return self.serialize_reservation(existing)

    def create_reservation(
        self,
        guest_id: UUID,
        room_type_id: int,
        check_in: date,
        check_out: date,
        num_guests: int,
        request_id: UUID,
        expected_total_price: Decimal,
        confirmed: bool = False
    ):

        if not confirmed:
            raise ValueError(
                "Guest confirmation is required."
            )

        # Return the original result if this request
        # has already been processed.
        existing = self._check_existing_request(
            request_id,
            guest_id,
            room_type_id,
            check_in,
            check_out,
            num_guests,
            expected_total_price
        )

        if existing is not None:
            return existing

        today = datetime.now(
            ZoneInfo("Asia/Colombo")
        ).date()

        # Validate reservation dates.
        if check_in < today:
            raise ValueError(
                "Check-in cannot be in the past."
            )

        if check_out <= check_in:
            raise ValueError(
                "Check-out must be after check-in."
            )

        if num_guests <= 0:
            raise ValueError(
                "Number of guests must be positive."
            )

        # Validate guest.
        guest = self.guest_repository.get_by_id(
            guest_id
        )

        if guest is None:
            raise ValueError("Guest not found.")

        # Validate room category.
        category = self.room_repository.get_room_type_by_id(
            room_type_id
        )

        if category is None:
            raise ValueError("Room type not found.")

        if num_guests > category.max_guests:
            raise ValueError(
                "Guest count exceeds room capacity."
            )

        # Recheck room availability.
        available_rooms = (
            self.room_repository.get_available_rooms(
                check_in=check_in,
                check_out=check_out,
                num_guests=num_guests,
                room_type=category.name
            )
        )

        if not available_rooms:
            raise ValueError(
                "No rooms available for the selected dates."
            )

        # Automatically allocate an available room.
        selected_room, selected_category = available_rooms[0]

        nights = (check_out - check_in).days

        price_per_night = selected_category.price_per_night

        total_price = price_per_night * nights

        # Verify that the guest confirmed the current price.
        if total_price != expected_total_price:
            raise ValueError(
                "The price has changed. "
                "Please confirm the updated price."
            )

        reservation = Reservation(
            id=request_id,
            booking_reference=self.generate_booking_reference(
                request_id
            ),
            guest_id=guest.id,
            room_id=selected_room.id,
            check_in=check_in,
            check_out=check_out,
            num_guests=num_guests,
            price_per_night=price_per_night,
            total_price=total_price,
            status="confirmed"
        )

        try:

            self.reservation_repository.create(reservation)

            self.db.commit()

            return self.serialize_reservation(reservation)

        except IntegrityError as error:

            self.db.rollback()

            # Handle concurrent retries of the same request.
            existing = self._check_existing_request(
                request_id,
                guest_id,
                room_type_id,
                check_in,
                check_out,
                num_guests,
                expected_total_price
            )

            if existing is not None:
                return existing

            raise ValueError(
                "Reservation conflict. "
                "Please check availability again."
            ) from error

        except Exception:

            self.db.rollback()
            raise

    def get_reservation(
            self,
            booking_reference: str,
            guest_id: UUID
    ):

        booking_reference = booking_reference.strip().upper()

        reservation = (
            self.reservation_repository.get_by_reference(
                booking_reference,
                guest_id
            )
        )

        if reservation is None:
            raise ValueError("Reservation not found.")

        result = self.serialize_reservation(reservation)

        room = self.room_repository.get_room_by_id(
            reservation.room_id
        )

        if room is not None:
            category = (
                self.room_repository.get_room_type_by_id(
                    room.room_type_id
                )
            )

            result["room_number"] = room.room_number

            result["room_type"] = (
                category.name if category else None
            )

        return result

    def cancel_reservation(
            self,
            booking_reference: str,
            guest_id: UUID,
            confirmed: bool = False
    ):

        if not confirmed:
            raise ValueError(
                "Cancellation confirmation is required."
            )

        booking_reference = booking_reference.strip().upper()

        try:

            reservation = (
                self.reservation_repository.get_by_reference(
                    booking_reference,
                    guest_id,
                    for_update=True
                )
            )

            if reservation is None:
                raise ValueError("Reservation not found.")

            if reservation.status == "cancelled":
                self.db.commit()

                return self.serialize_reservation(reservation)

            if reservation.status != "confirmed":
                raise ValueError(
                    f"Cannot cancel a reservation with "
                    f"status '{reservation.status}'."
                )

            self.reservation_repository.cancel(reservation)

            self.db.commit()

            return self.serialize_reservation(reservation)

        except Exception:

            self.db.rollback()
            raise

