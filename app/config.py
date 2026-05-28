from functools import lru_cache
from pydantic import BaseModel
import os


class Settings(BaseModel):
    environment: str = "local"
    payment_provider_base_url: str = "https://payments.example.internal"
    payment_provider_api_key: str = "local-dev-key"
    payment_provider_timeout_seconds: float = 3.0


@lru_cache
def get_settings() -> Settings:
    return Settings(
        environment=os.getenv("PAYMENTS_ENV", "local"),
        payment_provider_base_url=os.getenv(
            "PAYMENT_PROVIDER_BASE_URL", "https://payments.example.internal"
        ),
        payment_provider_api_key=os.getenv("PAYMENT_PROVIDER_API_KEY", "local-dev-key"),
        payment_provider_timeout_seconds=float(
            os.getenv("PAYMENT_PROVIDER_TIMEOUT_SECONDS", "3.0")
        ),
    )
