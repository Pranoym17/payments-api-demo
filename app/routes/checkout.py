from fastapi import APIRouter, HTTPException, status

from app.models.payment import PaymentRequest, PaymentResponse, PaymentStatus
from app.services.idempotency import idempotency_store
from app.services.payment_gateway import PaymentGateway

router = APIRouter(tags=["checkout"])


@router.post("/checkout", response_model=PaymentResponse)
async def checkout(payment: PaymentRequest) -> PaymentResponse:
    cached = idempotency_store.get(payment.idempotency_key)
    if cached:
        return cached

    result = await PaymentGateway().authorize(payment)

    if result.status == PaymentStatus.failed:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=result.message,
        )

    idempotency_store.put(payment.idempotency_key, result)
    return result
