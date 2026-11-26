from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models import ServiceRequest, Reservation


class ServiceRequestRepository:

    def __init__(self, db: Session):

        self.db = db

    def get_by_id(
        self,
        request_id: UUID,
        guest_id: UUID,
        for_update: bool = False
    ):

        stmt = (
            select(ServiceRequest)
            .join(
                Reservation,
                ServiceRequest.reservation_id == Reservation.id
            )
            .where(
                ServiceRequest.id == request_id,
                Reservation.guest_id == guest_id
            )
        )

        if for_update:
            stmt = stmt.with_for_update(of=ServiceRequest)

        return self.db.scalars(stmt).one_or_none()

    def get_by_guest(self, guest_id: UUID):

        stmt = (
            select(ServiceRequest)
            .join(
                Reservation,
                ServiceRequest.reservation_id == Reservation.id
            )
            .where(
                Reservation.guest_id == guest_id
            )
            .order_by(ServiceRequest.created_at.desc())
        )

        return self.db.scalars(stmt).all()

    def create(self, service_request: ServiceRequest):

        self.db.add(service_request)

        self.db.flush()

        return service_request

    def cancel(self, service_request: ServiceRequest):

        service_request.status = "cancelled"

        self.db.flush()

        return service_request
