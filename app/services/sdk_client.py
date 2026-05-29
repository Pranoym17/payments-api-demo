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

# SentinelAI suggested fix preview
# Review before merging. Generated from incident context.
# --- a/app/services/sdk_client.py
# +++ b/app/services/sdk_client.py
# @@ ... @@
# -import requests
# +import requests
# 
# -class SDKClient:
# -    def __init__(self, base_url):
# -        self.base_url = base_url
# -
# -    def authenticate(self, username, password):
# -        response = requests.post(
# -            f"{self.base_url}/auth",
# -            json={"username": username, "password": password}
# -        )
# -        response.raise_for_status()
# -        return response.json()
# +class SDKClient:
# +    def __init__(self, base_url):
# +        self.base_url = base_url
# +
# +    def authenticate(self, username, password):
# +        response = requests.post(
# +            f"{self.base_url}/auth",
# +            json={"username": username, "password": password},
# +            timeout=2
# +        )
# +        response.raise_for_status()
# +        return response.json()
