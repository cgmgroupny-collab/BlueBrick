// POST /api/stripe-webhook
// Receives Stripe events, verifies signature, appends to bookings.json,
// triggers transactional emails via the Python helper.
//
// ENV VARS:
//   STRIPE_SECRET_KEY      — required for Stripe SDK calls (customer lookup)
//   STRIPE_WEBHOOK_SECRET  — whsec_... from the Stripe Dashboard endpoint
//   GMAIL_USER / GMAIL_APP_PASSWORD — used by send_booking_email.py (not read here)
//
// Setup:
//   1. Deploy to Vercel.
//   2. Stripe Dashboard → Developers → Webhooks → Add endpoint
//      URL: https://bluebrickcleaning.com/api/stripe-webhook
//      Events: checkout.session.completed,
//              customer.subscription.created,
//              customer.subscription.deleted,
//              invoice.payment_succeeded,
//              invoice.payment_failed
//   3. Copy the "Signing secret" (whsec_...) into Vercel env as STRIPE_WEBHOOK_SECRET.

const Stripe = require("stripe");
const fs = require("fs");
const path = require("path");
const { exec } = require("child_process");

// IMPORTANT: Vercel must pass the raw body for signature verification.
// Disable the default body parser for this route.
module.exports.config = { api: { bodyParser: false } };

function stripeClient() {
  const key = process.env.STRIPE_SECRET_KEY;
  if (!key) throw new Error("STRIPE_SECRET_KEY not set");
  return new Stripe(key, { apiVersion: "2024-06-20" });
}

async function readRawBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on("data", (c) => chunks.push(Buffer.isBuffer(c) ? c : Buffer.from(c)));
    req.on("end", () => resolve(Buffer.concat(chunks)));
    req.on("error", reject);
  });
}

// --- Booking persistence ---------------------------------------------------
// TODO(prod): swap to Vercel Blob (`@vercel/blob`) or a real DB.
// The filesystem write only works in local/dev; Vercel production FS is read-only
// except /tmp. For now we write to /tmp in production and fall back to the
// repo's data/bookings.json in dev so local dev sees new records.
function bookingsFilePath() {
  if (process.env.VERCEL) return "/tmp/bookings.json";
  return path.resolve(process.cwd(), "data", "bookings.json");
}

function loadBookings() {
  const p = bookingsFilePath();
  try {
    if (!fs.existsSync(p)) return [];
    return JSON.parse(fs.readFileSync(p, "utf8"));
  } catch (e) {
    console.error("[webhook] failed to read bookings.json", e);
    return [];
  }
}

function saveBookings(list) {
  const p = bookingsFilePath();
  try {
    fs.mkdirSync(path.dirname(p), { recursive: true });
    fs.writeFileSync(p, JSON.stringify(list, null, 2));
  } catch (e) {
    console.error("[webhook] failed to write bookings.json", e);
  }
}

function upsertBooking(record) {
  const list = loadBookings();
  // Idempotency by stripe_event_id + session_id.
  const existingIdx = list.findIndex(
    (b) => b.stripe_session_id && b.stripe_session_id === record.stripe_session_id
  );
  if (existingIdx >= 0) {
    list[existingIdx] = { ...list[existingIdx], ...record, updated_at: new Date().toISOString() };
  } else {
    list.unshift({ ...record, created_at: new Date().toISOString() });
  }
  saveBookings(list);
}

// --- Email trigger ---------------------------------------------------------
// Integration point: the email agent delivers /tools/booking-emails/send_booking_email.py
// with signature: python3 send_booking_email.py --template <name> --to <email> --json '<payload>'
function triggerEmail(template, to, payload) {
  const script = path.resolve(process.cwd(), "tools", "booking-emails", "send_booking_email.py");
  if (!fs.existsSync(script)) {
    console.warn(`[webhook] email script missing, skipped ${template} → ${to}`);
    return;
  }
  const json = JSON.stringify(payload).replace(/'/g, "'\\''");
  const cmd = `python3 -u "${script}" --template ${template} --to "${to}" --json '${json}'`;
  exec(cmd, { timeout: 15000 }, (err, stdout, stderr) => {
    if (err) console.error(`[webhook] email ${template} failed:`, stderr || err.message);
    else console.log(`[webhook] email ${template} → ${to} ok`);
  });
}

// --- Event handlers --------------------------------------------------------
function handleCheckoutCompleted(session) {
  const record = {
    stripe_session_id: session.id,
    stripe_customer_id: session.customer || null,
    stripe_subscription_id: session.subscription || null,
    stripe_payment_intent_id: session.payment_intent || null,
    mode: session.mode, // "payment" | "subscription"
    status: "confirmed",
    customer_email: session.customer_details?.email || session.customer_email || null,
    customer_name: session.customer_details?.name || null,
    customer_phone: session.customer_details?.phone || null,
    amount_total: session.amount_total, // cents
    currency: session.currency,
    service: session.metadata?.service || null,
    addons: (session.metadata?.addons || "").split(",").filter(Boolean),
    zip: session.metadata?.zip || null,
    visit_date: session.metadata?.visit_date || null,
    address:
      session.customer_details?.address
        ? [
            session.customer_details.address.line1,
            session.customer_details.address.line2,
            session.customer_details.address.city,
            session.customer_details.address.state,
            session.customer_details.address.postal_code,
          ]
            .filter(Boolean)
            .join(", ")
        : null,
  };
  upsertBooking(record);

  if (record.customer_email) {
    triggerEmail("welcome", record.customer_email, {
      name: record.customer_name,
      service: record.service,
      visit_date: record.visit_date,
      amount: record.amount_total,
      mode: record.mode,
    });
  }
}

function handleSubscriptionCreated(sub) {
  upsertBooking({
    stripe_session_id: `sub_${sub.id}`,
    stripe_subscription_id: sub.id,
    stripe_customer_id: sub.customer,
    mode: "subscription",
    status: sub.status, // "active" | "trialing" | ...
    service: sub.metadata?.service || "monthly",
    current_period_end: sub.current_period_end
      ? new Date(sub.current_period_end * 1000).toISOString()
      : null,
  });
}

function handleSubscriptionDeleted(sub) {
  upsertBooking({
    stripe_session_id: `sub_${sub.id}`,
    stripe_subscription_id: sub.id,
    stripe_customer_id: sub.customer,
    mode: "subscription",
    status: "cancelled",
    cancelled_at: new Date().toISOString(),
  });
}

async function handleInvoicePaid(invoice) {
  const email = invoice.customer_email;
  if (email) {
    triggerEmail("renewal_receipt", email, {
      amount: invoice.amount_paid,
      invoice_number: invoice.number,
      period_end: invoice.period_end,
      hosted_invoice_url: invoice.hosted_invoice_url,
    });
  }
}

async function handleInvoiceFailed(invoice) {
  const email = invoice.customer_email;
  if (email) {
    triggerEmail("payment_failed", email, {
      amount: invoice.amount_due,
      invoice_number: invoice.number,
      hosted_invoice_url: invoice.hosted_invoice_url,
    });
  }
}

// --- Main handler ----------------------------------------------------------
module.exports = async (req, res) => {
  if (req.method !== "POST") return res.status(405).json({ error: "Method not allowed" });

  const sig = req.headers["stripe-signature"];
  const whSecret = process.env.STRIPE_WEBHOOK_SECRET;
  if (!sig || !whSecret) {
    console.error("[webhook] missing signature or STRIPE_WEBHOOK_SECRET");
    return res.status(400).send("Missing signature");
  }

  let event;
  try {
    const raw = await readRawBody(req);
    const stripe = stripeClient();
    event = stripe.webhooks.constructEvent(raw, sig, whSecret);
  } catch (err) {
    console.error("[webhook] signature verification failed:", err.message);
    return res.status(400).send(`Webhook Error: ${err.message}`);
  }

  try {
    switch (event.type) {
      case "checkout.session.completed":
        handleCheckoutCompleted(event.data.object);
        break;
      case "customer.subscription.created":
        handleSubscriptionCreated(event.data.object);
        break;
      case "customer.subscription.deleted":
        handleSubscriptionDeleted(event.data.object);
        break;
      case "invoice.payment_succeeded":
        await handleInvoicePaid(event.data.object);
        break;
      case "invoice.payment_failed":
        await handleInvoiceFailed(event.data.object);
        break;
      default:
        // Ignore unhandled events (but still 200 so Stripe stops retrying).
        console.log(`[webhook] ignored event: ${event.type}`);
    }
  } catch (err) {
    console.error(`[webhook] handler error for ${event.type}:`, err);
    // Return 500 so Stripe retries (only for handler bugs, not signature issues).
    return res.status(500).json({ error: "handler failed" });
  }

  return res.status(200).json({ received: true });
};
