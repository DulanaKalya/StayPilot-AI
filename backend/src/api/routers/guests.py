from fastapi import APIRouter

from src.api.dependencies import (
    DatabaseSession,
    CurrentGuest
)

from src.api.errors import call_service

from src.schemas.guest import (
    GuestCreate,
    GuestUpdate
)

from src.services.guest_service import GuestService


router = APIRouter(
    prefix="/guests",
    tags=["Guests"]
)


@router.post("", status_code=201)
def create_guest(
    payload: GuestCreate,
    db: DatabaseSession,
    guest_id: CurrentGuest
):

    service = GuestService(db)

    return call_service(
        service.create_guest,
        **payload.model_dump()
    )


@router.get("/me")
def get_current_guest_details(
    db: DatabaseSession,
    guest_id: CurrentGuest
):

    service = GuestService(db)

    return call_service(
        service.get_guest_by_id,
        guest_id,
        error_status=404
    )


@router.patch("/me")
def update_guest(
    payload: GuestUpdate,
    db: DatabaseSession,
    guest_id: CurrentGuest
):

    service = GuestService(db)

    return call_service(
        service.update_guest,
        guest_id=guest_id,
        **payload.model_dump(exclude_unset=True)
    )
