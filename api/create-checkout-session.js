// POST /api/create-checkout-session
// Creates a Stripe Checkout Session for the Blue Brick booking wizard.
//
// Request body (JSON):
//   {
//     service:        "onetime" | "monthly" | "commercial",
//     frequency:      "onetime" | "monthly",                // informational; service is source of truth
//     addons:         ["window","oven","laundry","bin"],    // optional
//     customer_email: "jane@example.com",
//     zip:            "02116",
//     visit_date:     "2026-04-22"                          // ISO date, optional
//   }
//
// Response: { url: "https://checkout.stripe.com/..." }
//
// ENV VARS (set in Vercel project settings):
//   STRIPE_SECRET_KEY        — sk_live_... or sk_test_...
//   PUBLIC_SITE_URL          — https://bluebrickcleaning.com (optional; falls back to request origin)
//
// Apple Pay + Google Pay: enabled automatically by Stripe Checkout when
// `payment_method_types` includes "card" (or is omitted) and the merchant
// has Apple Pay domain-verification on bluebrickcleaning.com.

const Stripe = require("stripe");
const { SERVICES, ADDONS } = require("./_catalog");

// Lazy-init so the file loads even when the env var is missing (better error).
function stripeClient() {
  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) throw new Error("STRIPE_SECRET_KEY not set");
  return new Stripe(key, { apiVersion: "2024-06-20" });
}

function setCors(req, res) {
  // Same-origin in prod; allow localhost for dev. Lock down with explicit origin if needed.
  const origin = req.headers.origin || "";
  const allow =
    /^https?:\/\/(localhost(:\d+)?|127\.0\.0\.1(:\d+)?|([a-z0-9-]+\.)?bluebrickcleaning\.com)$/i.test(origin)
      ? origin
      : "*";
  res.setHeader("Access-Control-Allow-Origin", allow);
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  res.setHeader("Vary", "Origin");
}

module.exports = async (req, res) => {
  setCors(req, res);
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") {
    return res.status(405).json({ error: "Method not allowed" });
  }

  try {
    const body = typeof req.body === "string" ? JSON.parse(req.body) : (req.body || {});
    const {
      service,
      frequency,
      addons = [],
      customer_email,
      zip,
      visit_date,
    } = body;

    if (!service || !SERVICES[service]) {
      return res.status(400).json({ error: "Invalid service" });
    }
    if (!customer_email || !/.+@.+\..+/.test(customer_email)) {
      return res.status(400).json({ error: "Invalid email" });
    }

    const svc = SERVICES[service];
    const isSubscription = svc.recurring === true;

    // Build line items from server-side catalog (never trust client prices).
    const line_items = [
      {
        price_data: {
          currency: "usd",
          product_data: {
            name: svc.name,
            description: svc.description,
          },
          unit_amount: svc.amount,
          ...(isSubscription ? { recurring: { interval: svc.interval } } : {}),
        },
        quantity: 1,
      },
    ];

    // Add-ons: Stripe subscriptions require ALL recurring line items to
    // share the same interval. We charge add-ons as a recurring line with
    // matching interval for subs, and one-off for payment mode.
    for (const key of Array.isArray(addons) ? addons : []) {
      const addon = ADDONS[key];
      if (!addon) continue;
      line_items.push({
        price_data: {
          currency: "usd",
          product_data: { name: addon.name },
          unit_amount: addon.amount,
          ...(isSubscription ? { recurring: { interval: svc.interval } } : {}),
        },
        quantity: 1,
      });
    }

    const origin =
      process.env.PUBLIC_SITE_URL ||
      (req.headers.origin ? req.headers.origin : "https://bluebrickcleaning.com");

    // Idempotency: if the client retries with the same email+service+visit+addons,
    // Stripe will return the same session instead of creating duplicates.
    const idempotencyKey = [
      customer_email.toLowerCase(),
      service,
      visit_date || "no-date",
      (addons || []).slice().sort().join(","),
    ].join("|");

    const stripe = stripeClient();
    const session = await stripe.checkout.sessions.create(
      {
        mode: isSubscription ? "subscription" : "payment",
        line_items,
        customer_email,
        allow_promotion_codes: true,
        billing_address_collection: "required",
        phone_number_collection: { enabled: true },
        automatic_tax: { enabled: false }, // flip on once Stripe Tax is live
        // Apple Pay / Google Pay ride on "card" automatically.
        payment_method_types: ["card"],
        success_url: `${origin}/booking-confirmed/?session_id={CHECKOUT_SESSION_ID}`,
        cancel_url: `${origin}/book/`,
        metadata: {
          service,
          frequency: frequency || (isSubscription ? "monthly" : "onetime"),
          addons: (addons || []).join(","),
          zip: zip || "",
          visit_date: visit_date || "",
        },
        ...(isSubscription
          ? {
              subscription_data: {
                metadata: {
                  service,
                  zip: zip || "",
                  visit_date: visit_date || "",
                },
              },
            }
          : {
              payment_intent_data: {
                metadata: {
                  service,
                  zip: zip || "",
                  visit_date: visit_date || "",
                },
              },
            }),
      },
      { idempotencyKey }
    );

    return res.status(200).json({ id: session.id, url: session.url });
  } catch (err) {
    console.error("[create-checkout-session]", err);
    return res.status(500).json({
      error: "Stripe error",
      message: err.message || String(err),
    });
  }
};
