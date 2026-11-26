from uuid import UUID
from datetime import datetime
from zoneinfo import ZoneInfo

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from src.database.models import ServiceRequest

from src.database.repositories.reservation_repository import (
    ReservationRepository
)

from src.database.repositories.service_request_repository import (
    ServiceRequestRepository
)


class GuestRequestService:

    ALLOWED_SERVICE_TYPES = {
        "housekeeping",
        "room_service",
        "amenities",
        "transport",
        "maintenance",
        "other"
    }

    def __init__(self, db: Session):

        self.db = db

        self.reservation_repository = ReservationRepository(db)

        self.service_request_repository = (
            ServiceRequestRepository(db)
        )

    @staticmethod
    def serialize_request(request):

        return {
            "request_id": str(request.id),
            "reservation_id": str(request.reservation_id),
            "service_type": request.service_type,
            "description": request.description,
            "status": request.status,
            "created_at": request.created_at.isoformat(),
            "updated_at": request.updated_at.isoformat()
        }

    def _check_existing_request(
        self,
        request_id: UUID,
        guest_id: UUID,
        reservation_id: UUID,
        service_type: str,
        description: str
    ):

        existing = self.service_request_repository.get_by_id(
            request_id,
            guest_id
        )

        if existing is None:
            return None

        if (
            existing.reservation_id != reservation_id
            or existing.service_type != service_type
            or existing.description != description
        ):
            raise ValueError(
                "Request ID conflicts with an existing request."
            )

        return self.serialize_request(existing)

    def create_service_request(
        self,
        guest_id: UUID,
        booking_reference: str,
        service_type: str,
        description: str,
        request_id: UUID,
        confirmed: bool = False
    ):

        if not confirmed:
            raise ValueError(
                "Guest confirmation is required."
            )

        service_type = service_type.strip().lower()

        description = description.strip()

        booking_reference = (
            booking_reference.strip().upper()
        )

        # Validate service type.
        if service_type not in self.ALLOWED_SERVICE_TYPES:
            raise ValueError("Invalid service type.")

        # Validate description.
        if not description or len(description) > 1000:
            raise ValueError("Invalid request description.")

        # Retrieve the guest's reservation.
        reservation = (
            self.reservation_repository.get_by_reference(
                booking_reference,
                guest_id
            )
        )

        if reservation is None:
            raise ValueError("Reservation not found.")

        # Check idempotency.
        existing = self._check_existing_request(
            request_id,
            guest_id,
            reservation.id,
            service_type,
            description
        )

        if existing is not None:
            return existing

        today = datetime.now(
            ZoneInfo("Asia/Colombo")
        ).date()

        # Verify an active hotel stay.
        if (
            reservation.status != "checked_in"
            or not (
                reservation.check_in
                <= today
                < reservation.check_out
            )
        ):
            raise ValueError(
                "An active hotel stay is required."
            )

        service_request = ServiceRequest(
            id=request_id,
            reservation_id=reservation.id,
            service_type=service_type,
            description=description,
            status="pending"
        )

        reservation_id = reservation.id

        try:

            self.service_request_repository.create(
                service_request
            )

            self.db.commit()

            return self.serialize_request(service_request)

        except IntegrityError as error:

            self.db.rollback()

            existing = self._check_existing_request(
                request_id,
                guest_id,
                reservation_id,
                service_type,
                description
            )

            if existing is not None:
                return existing

            raise ValueError(
                "Unable to create service request."
            ) from error

        except Exception:

            self.db.rollback()
            raise

    def get_service_request(
        self,
        request_id: UUID,
        guest_id: UUID
    ):

        request = self.service_request_repository.get_by_id(
            request_id,
            guest_id
        )

        if request is None:
            raise ValueError("Service request not found.")

        return self.serialize_request(request)

    def get_guest_requests(self, guest_id: UUID):

        requests = (
            self.service_request_repository.get_by_guest(
                guest_id
            )
        )

        return {
            "guest_id": str(guest_id),
            "total_requests": len(requests),
            "requests": [
                self.serialize_request(request)
                for request in requests
            ]
        }

    def cancel_service_request(
        self,
        request_id: UUID,
        guest_id: UUID,
        confirmed: bool = False
    ):

        if not confirmed:
            raise ValueError(
                "Cancellation confirmation is required."
            )

        try:

            request = (
                self.service_request_repository.get_by_id(
                    request_id,
                    guest_id,
                    for_update=True
                )
            )

            if request is None:
                raise ValueError("Service request not found.")

            if request.status == "cancelled":

                self.db.commit()

                return self.serialize_request(request)

            if request.status != "pending":
                raise ValueError(
                    "Only pending requests can be cancelled."
                )

            self.service_request_repository.cancel(request)

            self.db.commit()

            return self.serialize_request(request)

        except Exception:

            self.db.rollback()
            raise
