import json

from uuid import UUID

from src.database.connection import SessionLocal
from src.services.guest_service import GuestService


def main():

    with SessionLocal() as db:

        service = GuestService(db)

        # Test 1: Retrieve existing guest by email
        guest = service.get_guest_by_email(
            "kavindu.perera@example.com"
        )

        print("\n--- GUEST DETAILS ---")

        print(json.dumps(guest, indent=4))

        # Test 2: Retrieve guest by phone
        if guest["phone"]:

            result = service.get_guest_by_phone(
                guest["phone"]
            )

            print("\n--- PHONE SEARCH ---")

            print(json.dumps(result, indent=4))

        # Test 3: Retrieve booking history
        history = service.get_booking_history(
            UUID(guest["guest_id"])
        )

        print("\n--- BOOKING HISTORY ---")

        print(json.dumps(history, indent=4))


if __name__ == "__main__":
    main()
