import json

from uuid import UUID, uuid4

from src.database.connection import SessionLocal
from src.services.guest_service import GuestService
from src.services.guest_request_service import GuestRequestService


def main():

    with SessionLocal() as db:

        guest_service = GuestService(db)

        request_service = GuestRequestService(db)

        guest = guest_service.get_guest_by_email(
            "kavindu.perera@example.com"
        )

        guest_id = UUID(guest["guest_id"])

        request_id = uuid4()

        params = {
            "guest_id": guest_id,
            "booking_reference": "SP-DEMO-001",
            "service_type": "room_service",
            "description": (
                "Please send two cups of Ceylon tea "
                "and a plate of vegetable kottu."
            ),
            "request_id": request_id,
            "confirmed": True
        }

        # Test 1: Create service request.
        request = request_service.create_service_request(
            **params
        )

        print("\n--- SERVICE REQUEST CREATED ---")
        print(json.dumps(request, indent=4))

        assert request["status"] == "pending"

        # Test 2: Retry the same request.
        repeated_request = (
            request_service.create_service_request(
                **params
            )
        )

        assert (
            request["request_id"]
            == repeated_request["request_id"]
        )

        print("\nIdempotency test passed!")

        # Test 3: Retrieve service request.
        details = request_service.get_service_request(
            request_id=request_id,
            guest_id=guest_id
        )

        print("\n--- REQUEST DETAILS ---")
        print(json.dumps(details, indent=4))

        # Test 4: Retrieve guest requests.
        requests = request_service.get_guest_requests(
            guest_id=guest_id
        )

        print("\n--- ALL GUEST REQUESTS ---")
        print(json.dumps(requests, indent=4))

        # Test 5: Cancel service request.
        cancelled = request_service.cancel_service_request(
            request_id=request_id,
            guest_id=guest_id,
            confirmed=True
        )

        assert cancelled["status"] == "cancelled"

        print("\n--- REQUEST CANCELLED ---")
        print(json.dumps(cancelled, indent=4))

        print("\nAll service request checks passed!")


if __name__ == "__main__":
    main()
