// POST /api/get-customer-portal
// Creates a Stripe Billing Portal session for a logged-in customer.
//
// Request body: { customer_id: "cus_..." }   OR   { email: "jane@example.com" }
// Response:     { url: "https://billing.stripe.com/..." }
//
// ENV VARS:
//   STRIPE_SECRET_KEY  — required
//   PUBLIC_SITE_URL    — return_url base (falls back to request origin)

const Stripe = require("stripe");

function stripeClient() {
  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) throw new Error("STRIPE_SECRET_KEY not set");
  return new Stripe(key, { apiVersion: "2024-06-20" });
}

function setCors(req, res) {
  const origin = req.headers.origin || "";
  const allow =
    /^https?:\/\/(localhost(:\d+)?|127\.0\.0\.1(:\d+)?|([a-z0-9-]+\.)?bluebrickcleaning\.com)$/i.test(origin)
      ? origin
      : "*";
  res.setHeader("Access-Control-Allow-Origin", allow);
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
}

module.exports = async (req, res) => {
  setCors(req, res);
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  try {
    const body = typeof req.body === "string" ? JSON.parse(req.body) : (req.body || {});
    let { customer_id, email } = body;

    const stripe = stripeClient();

    // If only email is given, look up the customer.
    if (!customer_id && email) {
      const list = await stripe.customers.list({ email, limit: 1 });
      if (!list.data.length) {
        return res.status(404).json({ error: "No Stripe customer with that email" });
      }
      customer_id = list.data[0].id;
    }

    if (!customer_id) {
      return res.status(400).json({ error: "customer_id or email required" });
    }

    const origin =
      process.env.PUBLIC_SITE_URL ||
      req.headers.origin ||
      "https://bluebrickcleaning.com";

    const session = await stripe.billingPortal.sessions.create({
      customer: customer_id,
      return_url: `${origin}/dashboard/`,
    });

    return res.status(200).json({ url: session.url });
  } catch (err) {
    console.error("[get-customer-portal]", err);
    return res.status(500).json({ error: "Stripe error", message: err.message });
  }
};
