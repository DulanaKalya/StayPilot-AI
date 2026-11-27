from uuid import UUID
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class ReservationCreate(BaseModel):

    room_type_id: int = Field(gt=0)

    check_in: date

    check_out: date

    num_guests: int = Field(gt=0)

    request_id: UUID

    expected_total_price: Decimal = Field(
        ge=0,
        max_digits=10,
        decimal_places=2
    )

    confirmed: bool = False


class CancellationRequest(BaseModel):

    confirmed: bool = False