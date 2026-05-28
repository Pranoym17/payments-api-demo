import httpx

from app.models.payment import PaymentRequest, PaymentResponse, PaymentStatus
from app.services.retry_policy import RetryPolicy
from app.services.sdk_client import PaymentProviderClient


class PaymentGateway:
    def __init__(
        self,
        client: PaymentProviderClient | None = None,
        retry_policy: RetryPolicy | None = None,
    ) -> None:
        self.client = client or PaymentProviderClient()
        self.retry_policy = retry_policy or RetryPolicy()

    async def authorize(self, payment: PaymentRequest) -> PaymentResponse:
        try:
            provider_response = await self.retry_policy.run(
                lambda: self.client.authorize(
                    order_id=payment.order_id,
                    amount=payment.amount,
                    currency=payment.currency,
                    card_token=payment.card.token,
                )
            )
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in {402, 409}:
                return PaymentResponse(
                    order_id=payment.order_id,
                    status=PaymentStatus.declined,
                    message="Payment was declined by provider",
                )
            return PaymentResponse(
                order_id=payment.order_id,
                status=PaymentStatus.failed,
                message="Payment provider returned an error",
            )
        except httpx.HTTPError:
            return PaymentResponse(
                order_id=payment.order_id,
                status=PaymentStatus.failed,
                message="Payment provider request failed",
            )

        if provider_response.get("status") == "authorized":
            authorization_id = provider_response.get("authorization_id")
            if not authorization_id:
                authorization_id = provider_response.get("auth", {}).get("id")

            return PaymentResponse(
                order_id=payment.order_id,
                status=PaymentStatus.authorized,
                authorization_id=authorization_id,
                message="Payment authorized",
            )

        return PaymentResponse(
            order_id=payment.order_id,
            status=PaymentStatus.declined,
            message=provider_response.get("message", "Payment was not authorized"),
        )
