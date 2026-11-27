from uuid import UUID

from fastapi import APIRouter

from src.api.dependencies import (
    DatabaseSession,
    CurrentGuest
)

from src.api.errors import call_service

from src.schemas.service_request import (
    ServiceRequestCreate
)

from src.schemas.reservation import (
    CancellationRequest
)

from src.services.guest_request_service import (
    GuestRequestService
)


router = APIRouter(
    prefix="/service-requests",
    tags=["Service Requests"]
)


@router.post("", status_code=201)
def create_service_request(
    payload: ServiceRequestCreate,
    db: DatabaseSession,
    guest_id: CurrentGuest
):

    service = GuestRequestService(db)

    return call_service(
        service.create_service_request,
        guest_id=guest_id,
        **payload.model_dump()
    )


@router.get("")
def get_guest_requests(
    db: DatabaseSession,
    guest_id: CurrentGuest
):

    service = GuestRequestService(db)

    return call_service(
        service.get_guest_requests,
        guest_id=guest_id
    )


@router.get("/{request_id}")
def get_service_request(
    request_id: UUID,
    db: DatabaseSession,
    guest_id: CurrentGuest
):

    service = GuestRequestService(db)

    return call_service(
        service.get_service_request,
        request_id=request_id,
        guest_id=guest_id,
        error_status=404
    )


@router.post("/{request_id}/cancel")
def cancel_service_request(
    request_id: UUID,
    payload: CancellationRequest,
    db: DatabaseSession,
    guest_id: CurrentGuest
):

    service = GuestRequestService(db)

    return call_service(
        service.cancel_service_request,
        request_id=request_id,
        guest_id=guest_id,
        confirmed=payload.confirmed
    )
