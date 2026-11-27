from datetime import datetime, timedelta
from uuid import uuid4
from zoneinfo import ZoneInfo

import httpx

from src.infrastructure.config import settings


BASE_URL = "http://127.0.0.1:8081"


def check(response, expected_status, message):

    assert response.status_code == expected_status, (
        f"{message}: Expected {expected_status}, "
        f"received {response.status_code}. "
        f"Response: {response.text}"
    )

    print(f"[PASS] {message}")

    return response.json()


def main():

    api_key = settings.demo_api_key.get_secret_value()

    headers = {
        "X-API-Key": api_key
    }

    today = datetime.now(
        ZoneInfo("Asia/Colombo")
    ).date()

    check_in = (today + timedelta(days=3)).isoformat()
    check_out = (today + timedelta(days=6)).isoformat()

    with httpx.Client(
        base_url=BASE_URL,
        timeout=30
    ) as client:

        # 1. Application health

        check(
            client.get("/health"),
            200,
            "Application health"
        )

        # 2. Retrieve room categories

        room_types = check(
            client.get("/api/v1/rooms/types"),
            200,
            "Retrieve room types"
        )

        assert len(room_types) == 5

        # 3. Check room availability

        availability = check(
            client.get(
                "/api/v1/rooms/availability",
                params={
                    "check_in": check_in,
                    "check_out": check_out,
                    "num_guests": 2,
                    "room_type": "Ocean View"
                }
            ),
            200,
            "Check room availability"
        )

        assert availability["available"]

        option = availability["options"][0]

        # 4. Invalid reservation dates

        check(
            client.get(
                "/api/v1/rooms/availability",
                params={
                    "check_in": check_out,
                    "check_out": check_in,
                    "num_guests": 2
                }
            ),
            400,
            "Reject invalid reservation dates"
        )

        # 5. Authentication check

        check(
            client.get("/api/v1/guests/me"),
            401,
            "Reject unauthenticated request"
        )

        # 6. Retrieve guest profile

        guest = check(
            client.get(
                "/api/v1/guests/me",
                headers=headers
            ),
            200,
            "Retrieve authenticated guest"
        )

        print(f"       Guest: {guest['full_name']}")

        # 7. Create reservation

        booking_payload = {
            "room_type_id": option["room_type_id"],
            "check_in": check_in,
            "check_out": check_out,
            "num_guests": 2,
            "request_id": str(uuid4()),
            "expected_total_price": option["total_price"],
            "confirmed": True
        }

        booking = check(
            client.post(
                "/api/v1/reservations",
                headers=headers,
                json=booking_payload
            ),
            201,
            "Create reservation"
        )

        reference = booking["booking_reference"]

        print(f"       Booking: {reference}")

        try:

            # 8. Verify idempotency

            repeated_booking = check(
                client.post(
                    "/api/v1/reservations",
                    headers=headers,
                    json=booking_payload
                ),
                201,
                "Retry reservation"
            )

            assert (
                booking["reservation_id"]
                == repeated_booking["reservation_id"]
            )

            print("[PASS] Reservation idempotency")

            # 9. Retrieve reservation

            details = check(
                client.get(
                    f"/api/v1/reservations/{reference}",
                    headers=headers
                ),
                200,
                "Retrieve reservation details"
            )

            assert details["status"] == "confirmed"

        finally:

            # 10. Cancel test reservation

            cancelled = check(
                client.post(
                    f"/api/v1/reservations/{reference}/cancel",
                    headers=headers,
                    json={"confirmed": True}
                ),
                200,
                "Cancel reservation"
            )

            assert cancelled["status"] == "cancelled"

        # 11. Find an active hotel stay

        history = check(
            client.get(
                "/api/v1/reservations",
                headers=headers
            ),
            200,
            "Retrieve booking history"
        )

        active_booking = next(
            (
                reservation
                for reservation in history["reservations"]
                if reservation["status"] == "checked_in"
                and reservation["check_in"]
                <= today.isoformat()
                < reservation["check_out"]
            ),
            None
        )

        if active_booking is None:

            print(
                "[SKIP] Service request tests: "
                "No active hotel stay."
            )

        else:

            request_id = str(uuid4())

            # 12. Create service request

            service_request = check(
                client.post(
                    "/api/v1/service-requests",
                    headers=headers,
                    json={
                        "booking_reference": (
                            active_booking["booking_reference"]
                        ),
                        "service_type": "room_service",
                        "description": (
                            "Please send two cups of Ceylon tea."
                        ),
                        "request_id": request_id,
                        "confirmed": True
                    }
                ),
                201,
                "Create guest service request"
            )

            try:

                assert service_request["status"] == "pending"

            finally:

                # 13. Cancel test service request

                cancelled_request = check(
                    client.post(
                        f"/api/v1/service-requests/{request_id}/cancel",
                        headers=headers,
                        json={"confirmed": True}
                    ),
                    200,
                    "Cancel guest service request"
                )

                assert cancelled_request["status"] == "cancelled"

        print("\nAll executed backend checks passed!")


if __name__ == "__main__":
    main()
