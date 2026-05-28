from decimal import Decimal
from typing import Any

import httpx

from app.config import get_settings


class PaymentProviderClient:
    def __init__(self) -> None:
        self.settings = get_settings()

    async def authorize(
        self,
        *,
        order_id: str,
        amount: Decimal,
        currency: str,
        card_token: str,
    ) -> dict[str, Any]:
        payload = {
            "merchant_order_id": order_id,
            "amount": str(amount),
            "currency": currency.upper(),
            "payment_method_token": card_token,
        }
        headers = {"Authorization": f"Bearer {self.settings.payment_provider_api_key}"}

        async with httpx.AsyncClient(
            base_url=self.settings.payment_provider_base_url,
            timeout=self.settings.payment_provider_timeout_seconds,
        ) as client:
            response = await client.post("/v1/authorizations", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return {
                "status": data["status"],
                "authorization_id": data["authorization_id"],
                "message": data.get("message", "authorization processed"),
            }
