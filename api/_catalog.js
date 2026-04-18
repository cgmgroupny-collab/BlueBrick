// Shared service + add-on catalog for Stripe checkout.
// Keep prices here (single source of truth) rather than trusting client.
// All amounts are in USD cents.

const SERVICES = {
  onetime: {
    key: "onetime",
    name: "One-Time Deep Cleaning",
    amount: 18900, // $189.00
    recurring: false,
    description: "One-time residential or small commercial clean.",
  },
  monthly: {
    key: "monthly",
    name: "Monthly Recurring Cleaning",
    amount: 12900, // $129.00 / visit
    recurring: true,
    interval: "month",
    description: "Recurring monthly visit. Cancel anytime.",
  },
  commercial: {
    key: "commercial",
    name: "Commercial Custom Quote (Deposit)",
    amount: 25000, // $250 deposit (applied to final quote)
    recurring: false,
    description: "Refundable deposit to hold your commercial walkthrough slot.",
  },
};

const ADDONS = {
  window: { key: "window", name: "Window Cleaning",  amount: 4900 },
  oven:   { key: "oven",   name: "Deep Oven Clean",  amount: 3900 },
  laundry:{ key: "laundry",name: "Laundry Room",     amount: 2900 },
  bin:    { key: "bin",    name: "Bin Cleaning",     amount: 3500 },
};

module.exports = { SERVICES, ADDONS };
