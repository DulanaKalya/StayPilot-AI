from pydantic import BaseModel, Field


class GuestCreate(BaseModel):

    full_name: str = Field(min_length=1, max_length=150)

    email: str = Field(min_length=3, max_length=255)

    phone: str | None = Field(default=None, max_length=30)


class GuestUpdate(BaseModel):

    full_name: str | None = Field(
        default=None,
        min_length=1,
        max_length=150
    )

    phone: str | None = Field(
        default=None,
        max_length=30
    )
