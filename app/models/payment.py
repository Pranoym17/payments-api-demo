from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field


class PaymentStatus(str, Enum):
    authorized = "authorized"
    declined = "declined"
    failed = "failed"


class CardDetails(BaseModel):
    token: str = Field(min_length=8)
    last4: str = Field(min_length=4, max_length=4)
    brand: str


class PaymentRequest(BaseModel):
    order_id: str
    customer_id: str
    amount: Decimal = Field(gt=0)
    currency: str = Field(min_length=3, max_length=3)
    card: CardDetails
    idempotency_key: str = Field(min_length=12)


class PaymentResponse(BaseModel):
    order_id: str
    status: PaymentStatus
    authorization_id: str | None = None
    message: str
