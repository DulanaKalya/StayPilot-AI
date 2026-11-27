from fastapi import APIRouter

from src.api.dependencies import (
    DatabaseSession,
    CurrentGuest
)

from src.api.errors import call_service

from src.schemas.reservation import (
    ReservationCreate,
    CancellationRequest
)

from src.services.reservation_service import (
    ReservationService
)

from src.services.guest_service import GuestService


router = APIRouter(
    prefix="/reservations",
    tags=["Reservations"]
)


@router.post("", status_code=201)
def create_reservation(
    payload: ReservationCreate,
    db: DatabaseSession,
    guest_id: CurrentGuest
):

    service = ReservationService(db)

    return call_service(
        service.create_reservation,
        guest_id=guest_id,
        **payload.model_dump()
    )


@router.get("")
def get_reservations(
    db: DatabaseSession,
    guest_id: CurrentGuest
):

    service = GuestService(db)

    return call_service(
        service.get_booking_history,
        guest_id
    )


@router.get("/{reference}")
def get_reservation(
    reference: str,
    db: DatabaseSession,
    guest_id: CurrentGuest
):

    service = ReservationService(db)

    return call_service(
        service.get_reservation,
        booking_reference=reference,
        guest_id=guest_id,
        error_status=404
    )


@router.post("/{reference}/cancel")
def cancel_reservation(
    reference: str,
    payload: CancellationRequest,
    db: DatabaseSession,
    guest_id: CurrentGuest
):

    service = ReservationService(db)

    return call_service(
        service.cancel_reservation,
        booking_reference=reference,
        guest_id=guest_id,
        confirmed=payload.confirmed
    )
