from fastapi import APIRouter, HTTPException

from groq import APIError, RateLimitError

from src.api.dependencies import CurrentGuest
from src.schemas.chat import ChatRequest, ChatResponse
from src.services.chat_service import ChatService


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


@router.post("", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    guest_id: CurrentGuest
):

    message = payload.message.strip()

    if not message:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    try:

        service = ChatService()

        response = await service.achat(message)

        return ChatResponse(
            response=response
        )

    except RateLimitError as error:

        raise HTTPException(
            status_code=429,
            detail="AI usage limit reached."
        ) from error

    except APIError as error:

        raise HTTPException(
            status_code=502,
            detail="AI provider is temporarily unavailable."
        ) from error