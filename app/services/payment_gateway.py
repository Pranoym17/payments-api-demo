import httpx

from app.models.payment import PaymentRequest, PaymentResponse, PaymentStatus
from app.observability.logging import get_logger
from app.services.retry_policy import RetryPolicy
from app.services.sdk_client import PaymentProviderClient

logger = get_logger(__name__)


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
                logger.info(
                    "payment_declined",
                    extra={"order_id": payment.order_id, "status_code": exc.response.status_code},
                )
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
            logger.exception("payment_provider_request_failed", extra={"order_id": payment.order_id})
            return PaymentResponse(
                order_id=payment.order_id,
                status=PaymentStatus.failed,
                message="Payment provider request failed",
            )

        if provider_response.get("status") == "authorized":
            authorization_id = provider_response["authorization_id"]

            logger.info(
                "payment_authorized",
                extra={"order_id": payment.order_id, "authorization_id": authorization_id},
            )
            return PaymentResponse(
                order_id=payment.order_id,
                status=PaymentStatus.authorized,
                authorization_id=authorization_id,
                message="Payment authorized",
            )

        logger.info("payment_not_authorized", extra={"order_id": payment.order_id})
        return PaymentResponse(
            order_id=payment.order_id,
            status=PaymentStatus.declined,
            message=provider_response.get("message", "Payment was not authorized"),
        )

# SentinelAI suggested fix preview
# Review before merging. Generated from incident context.
# --- a/app/services/payment_gateway.py
# +++ b/app/services/payment_gateway.py
# @@ ... @@
#  def process_payment(payment_request):
# -    sdk_response = sdk_client.charge(payment_request)
# -    # Assume sdk_response is a dict with 'status' and 'transaction_id'
# -    if sdk_response['status'] == 'success':
# -        return {
# -            'success': True,
# -            'transaction_id': sdk_response['transaction_id']
# -        }
# -    else:
# -        return {
# -            'success': False,
# -            'error': sdk_response.get('error', 'Unknown error')
# -        }
# +    sdk_response = sdk_client.charge(payment_request)
# +    # Defensive check for required fields
# +    if not isinstance(sdk_response, dict) or 'status' not in sdk_response:
# +        logger.error(f"Malformed SDK response: {sdk_response}")
# +        return {
# +            'success': False,
# +            'error': 'Internal error: malformed payment gateway response'
# +        }
# +    if sdk_response['status'] == 'success' and 'transaction_id' in sdk_response:
# +        return {
# +            'success': True,
# +            'transaction_id': sdk_response['transaction_id']
# +        }
# +    else:
# +        return {
# +            'success': False,
# +            'error': sdk_response.get('error', 'Unknown error')
# +        }
