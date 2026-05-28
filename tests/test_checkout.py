import asyncio
from decimal import Decimal

from app.models.payment import CardDetails, PaymentRequest, PaymentStatus
from app.services.payment_gateway import PaymentGateway


class StubProviderClient:
    def __init__(self, response):
        self.response = response

    async def authorize(self, **kwargs):
        return self.response


def payment_request() -> PaymentRequest:
    return PaymentRequest(
        order_id="ord_72418",
        customer_id="cus_9012",
        amount=Decimal("42.50"),
        currency="USD",
        card=CardDetails(token="tok_visa_4242", last4="4242", brand="visa"),
        idempotency_key="idem_20260527_001",
    )


def test_successful_checkout_authorization():
    gateway = PaymentGateway(
        StubProviderClient(
            {
                "status": "authorized",
                "authorization_id": "auth_987",
                "message": "approved",
            }
        )
    )

    response = asyncio.run(gateway.authorize(payment_request()))

    assert response.status == PaymentStatus.authorized
    assert response.authorization_id == "auth_987"


def test_failed_gateway_response():
    gateway = PaymentGateway(
        StubProviderClient(
            {
                "status": "declined",
                "message": "insufficient_funds",
            }
        )
    )

    response = asyncio.run(gateway.authorize(payment_request()))

    assert response.status == PaymentStatus.declined
    assert response.message == "insufficient_funds"
