# Payments API Demo

Internal demo service for checkout and billing authorization flows. The service exposes a small FastAPI surface that resembles a production payments API without requiring access to a real payment provider.

## Local Run

```bash
uvicorn app.main:app --reload
```

## Endpoints

- `GET /health` returns service readiness.
- `POST /checkout` authorizes a card payment for an order.

## Environment Variables

- `PAYMENTS_ENV` sets the runtime environment name. Defaults to `local`.
- `PAYMENT_PROVIDER_BASE_URL` sets the upstream provider URL.
- `PAYMENT_PROVIDER_API_KEY` configures provider authentication.
- `PAYMENT_PROVIDER_TIMEOUT_SECONDS` sets the SDK request timeout.

## Operational Notes

Checkout authorization is synchronous and depends on the upstream provider returning an authorization result. Payment provider SDK upgrades require careful rollout, response validation, and close monitoring of decline and error rates.
