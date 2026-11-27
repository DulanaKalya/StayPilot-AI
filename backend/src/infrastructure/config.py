from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal

ROOT_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):

    app_name: str = "StayPilot AI"
    app_env: str = "development"

    database_url: SecretStr

    demo_api_key: SecretStr | None = None

    demo_guest_email: str = "kavindu.perera@example.com"

    groq_api_key: SecretStr | None = None

    llm_model: str = "openai/gpt-oss-120b"

    llm_temperature: float = 0.2

    llm_max_tokens: int = 2048

    llm_timeout: int = 30

    llm_max_retries: int = 2

    llm_reasoning_effort: Literal[
        "low", "medium", "high"
    ] = "low"

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
