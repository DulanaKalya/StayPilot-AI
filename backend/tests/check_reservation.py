import json

from uuid import UUID, uuid4
from decimal import Decimal
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.database.connection import SessionLocal
from src.services.guest_service import GuestService
from src.services.reservation_service import ReservationService


def main():

    with SessionLocal() as db:

        guest_service = GuestService(db)

        reservation_service = ReservationService(db)

        guest = guest_service.get_guest_by_email(
            "kavindu.perera@example.com"
        )

        guest_id = UUID(guest["guest_id"])

        today = datetime.now(
            ZoneInfo("Asia/Colombo")
        ).date()

        check_in = today + timedelta(days=3)
        check_out = today + timedelta(days=6)

        # Test 1: Check availability.
        availability = reservation_service.check_availability(
            check_in=check_in,
            check_out=check_out,
            num_guests=2,
            room_type="Ocean View"
        )

        if not availability["available"]:
            raise RuntimeError("No rooms available for test.")

        option = availability["options"][0]

        request_id = uuid4()

        booking_params = {
            "guest_id": guest_id,
            "room_type_id": option["room_type_id"],
            "check_in": check_in,
            "check_out": check_out,
            "num_guests": 2,
            "request_id": request_id,
            "expected_total_price": Decimal(
                str(option["total_price"])
            ),
            "confirmed": True
        }

        # Test 2: Create reservation.
        booking = reservation_service.create_reservation(
            **booking_params
        )

        print("\n--- RESERVATION CREATED ---")
        print(json.dumps(booking, indent=4))

        reference = booking["booking_reference"]

        # Test 3: Retry same reservation.
        repeated_booking = (
            reservation_service.create_reservation(
                **booking_params
            )
        )

        assert (
            booking["reservation_id"]
            == repeated_booking["reservation_id"]
        )

        print("\nIdempotency test passed!")

        # Test 4: Retrieve reservation.
        details = reservation_service.get_reservation(
            booking_reference=reference,
            guest_id=guest_id
        )

        print("\n--- RESERVATION DETAILS ---")
        print(json.dumps(details, indent=4))

        # Test 5: Cancel reservation.
        cancelled = reservation_service.cancel_reservation(
            booking_reference=reference,
            guest_id=guest_id,
            confirmed=True
        )

        assert cancelled["status"] == "cancelled"

        print("\n--- RESERVATION CANCELLED ---")
        print(json.dumps(cancelled, indent=4))

        print("\nAll reservation checks passed!")


if __name__ == "__main__":
    main()
