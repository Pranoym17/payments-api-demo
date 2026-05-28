from app.models.payment import PaymentResponse


class IdempotencyStore:
    def __init__(self) -> None:
        self._responses: dict[str, PaymentResponse] = {}

    def get(self, key: str) -> PaymentResponse | None:
        return self._responses.get(key)

    def put(self, key: str, response: PaymentResponse) -> None:
        self._responses[key] = response


idempotency_store = IdempotencyStore()
