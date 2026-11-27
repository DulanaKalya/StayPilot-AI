from uuid import UUID
from typing import Literal

from pydantic import BaseModel, Field


class ServiceRequestCreate(BaseModel):

    booking_reference: str = Field(
        min_length=1,
        max_length=30
    )

    service_type: Literal[
        "housekeeping",
        "room_service",
        "amenities",
        "transport",
        "maintenance",
        "other"
    ]

    description: str = Field(
        min_length=1,
        max_length=1000
    )

    request_id: UUID

    confirmed: bool = False
