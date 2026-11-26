import json

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.services.reservation_service import (
    ReservationService
)
from src.database.connection import SessionLocal



def main():

    today = datetime.now(
        ZoneInfo("Asia/Colombo")
    ).date()

    with SessionLocal() as db:

        service = ReservationService(db)

        result = service.check_availability(
            check_in=today + timedelta(days=3),
            check_out=today + timedelta(days=6),
            num_guests=2,
            room_type="Ocean View"
        )

        print(
            json.dumps(
                result,
                indent=4,
                default=str
            )
        )


if __name__ == "__main__":
    main()
