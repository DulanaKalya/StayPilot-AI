from datetime import date

from fastapi import APIRouter, Query

from src.api.dependencies import DatabaseSession
from src.api.errors import call_service

from src.database.repositories.room_repository import (
    RoomRepository
)

from src.services.reservation_service import (
    ReservationService
)


router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"]
)


@router.get("/types")
def get_room_types(db: DatabaseSession):

    repository = RoomRepository(db)

    room_types = repository.get_all_room_types()

    return [
        {
            "id": room.id,
            "name": room.name,
            "description": room.description,
            "price_per_night": str(room.price_per_night),
            "currency": "USD",
            "max_guests": room.max_guests,
            "amenities": room.amenities
        }
        for room in room_types
    ]


@router.get("/availability")
def check_availability(
    check_in: date,
    check_out: date,
    db: DatabaseSession,
    num_guests: int = Query(gt=0),
    room_type: str | None = None
):

    service = ReservationService(db)

    result = call_service(
        service.check_availability,
        check_in=check_in,
        check_out=check_out,
        num_guests=num_guests,
        room_type=room_type
    )

    for option in result["options"]:

        option["price_per_night"] = str(
            option["price_per_night"]
        )

        option["total_price"] = str(
            option["total_price"]
        )

    return result
