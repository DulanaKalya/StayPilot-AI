import secrets

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import APIKeyHeader

from sqlalchemy.orm import Session

from src.database.connection import get_db
from src.infrastructure.config import settings

from src.database.repositories.guest_repository import (
    GuestRepository
)


DatabaseSession = Annotated[
    Session, Depends(get_db)
]


api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)


def get_current_guest(
    db: DatabaseSession,
    api_key: Annotated[
        str | None,
        Depends(api_key_header)
    ]
) -> UUID:

    configured_key = settings.demo_api_key

    if configured_key is None:
        raise HTTPException(
            status_code=503,
            detail="Demo authentication is not configured."
        )

    expected_key = configured_key.get_secret_value()

    if (
        not expected_key
        or not api_key
        or not secrets.compare_digest(
            api_key.encode(),
            expected_key.encode()
        )
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key."
        )

    repository = GuestRepository(db)

    guest = repository.get_by_email(
        settings.demo_guest_email
    )

    if guest is None:
        raise HTTPException(
            status_code=401,
            detail="Demo guest not found."
        )

    return guest.id


CurrentGuest = Annotated[
    UUID, Depends(get_current_guest)
]
