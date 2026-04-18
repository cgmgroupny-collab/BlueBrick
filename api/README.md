# Blue Brick — Booking API

Vercel serverless functions powering the booking wizard at `/book/` and the
customer dashboard at `/dashboard/`.

## Endpoints

| Method | Route                         | Purpose                                          |
|--------|-------------------------------|--------------------------------------------------|
| POST   | `/api/create-checkout-session`| Start a Stripe Checkout (one-time or monthly)    |
| POST   | `/api/stripe-webhook`         | Receive Stripe events, persist bookings, email   |
| POST   | `/api/get-customer-portal`    | Return a billing-portal URL for a customer       |

## Required environment variables (Vercel → Settings → Environment Variables)

| Name                     | Example                                  | Notes                                          |
|--------------------------|------------------------------------------|------------------------------------------------|
| `STRIPE_SECRET_KEY`      | `sk_live_…` / `sk_test_…`                | Server-side Stripe SDK key                     |
| `STRIPE_WEBHOOK_SECRET`  | `whsec_…`                                | Signing secret of the webhook endpoint below   |
| `GMAIL_USER`             | `hello@bluebrickcleaning.com`            | Used by `/tools/booking-emails/send_booking_email.py` |
| `GMAIL_APP_PASSWORD`     | 16-char Google app password              | Same                                           |
| `PUBLIC_SITE_URL`        | `https://bluebrickcleaning.com`          | Optional; used for success/cancel/return URLs  |

## Stripe webhook setup

1. Deploy the project to Vercel.
2. Open **Stripe Dashboard → Developers → Webhooks → Add endpoint**.
3. Endpoint URL:

       https://bluebrickcleaning.com/api/stripe-webhook

   (use the preview URL while testing)
4. Select these events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy the **Signing secret** (`whsec_…`) into Vercel as `STRIPE_WEBHOOK_SECRET`.
6. Redeploy so the new env var is picked up.

## Apple Pay / Google Pay

Enabled automatically by Stripe Checkout. For Apple Pay on the web, verify the
domain under **Stripe → Settings → Payment methods → Apple Pay → Add new domain**
(upload `apple-developer-merchantid-domain-association` to `/.well-known/` —
Stripe provides the file).

## Local development

    npm install
    vercel dev

Listen for webhooks locally:

    stripe listen --forward-to http://localhost:3000/api/stripe-webhook

Set `STRIPE_WEBHOOK_SECRET` to the `whsec_…` printed by `stripe listen`.

## Booking persistence

The webhook appends records to `data/bookings.json`:

- **Local:** writes to the repo `data/bookings.json` directly.
- **Vercel production:** writes to `/tmp/bookings.json` (ephemeral per-instance).
  TODO: swap for `@vercel/blob`, Upstash Redis, or Postgres. See the TODO in
  `stripe-webhook.js`.

## Email integration

Webhook calls `python3 tools/booking-emails/send_booking_email.py --template <name> --to <email> --json '<payload>'`.

Templates expected: `welcome`, `renewal_receipt`, `payment_failed`.
Owned by the email agent — this repo only invokes it.
