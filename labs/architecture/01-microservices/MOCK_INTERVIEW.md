# Mock Interview: Decomposing a Retail Monolith

> Candidate–interviewer transcript. Pinewood & Whiskers, an online pet-supplies shop, currently runs as a single deployable.

---

## Warm-Up

**Interviewer**: "Sales doubled this year, deploys hurt, and a bad search change can take the whole site down. Where do your service boundaries go?"

**Candidate**: "I'll name what already lives in the codebase: product facts and search, inventory, checkout, fulfilment, and customer loyalty. Five different change cadences and five different data owners — that's my candidate boundary list. I wouldn't cut all five on day one. Checkout and inventory leave first: checkout because it is latency-sensitive and failures there cost carts, inventory because it owns the one truly shared invariant — stock never goes negative."

**Interviewer**: "Why is inventory the fight?"

**Candidate**: "Today five features mutate `stock_qty` directly, and the invariant keeps getting broken. Giving that table a single owner ends the argument. Search is read-only over product facts; it can keep reading a replica for a quarter while we see how the seams hold."

**Interviewer**: "Checkout talks to inventory. Synchronous or not?"

**Candidate**: "The reservation is synchronous, with two properties. First, an idempotency key the client generates once per intended order. Second, a conditional decrement — `UPDATE stock SET qty = qty - ? WHERE sku = ? AND qty >= ?`. Zero rows updated means we lost the race, and the caller gets a 409 rather than a negative count. Everything after that — pick, pack, ship — flows through a bounded queue into the fulfilment service at its own pace."

**Interviewer**: "A shopper double-taps Pay and two requests arrive."

**Candidate**: "Both carry the same idempotency key, and the orders table has a unique index on it. The second insert loses; the caller receives the first confirmation verbatim. No charges twice, no phantom order."

**Interviewer**: "Loyalty then — extract it too?"

**Candidate**: "Not yet. Points accounting has one owner and a sleepy change cadence, so it stays a module until scaling or headcount argues otherwise. Extraction responds to pressure, never to a checklist."

**Interviewer**: "Weekly reports need orders joined against products."

**Candidate**: "Nightly export into the reporting store — not a shared schema. A cross-service `JOIN` is the shared-database coupling we just paid to remove, wearing nicer clothes."

**Interviewer**: "Anything that argues against all this?"

**Candidate**: "Yes: the operating bill. Every boundary adds on-call surface, tracing, and contract upkeep. With eight engineers I'd stop at three services and keep the rest as modules in one artifact. Decomposition follows the org chart at least as much as it follows the ER diagram."

---

## Probe Round

- "Inventory is down. What does checkout do?" — a short bounded wait, then an honest "try again shortly"; the fulfilment queue absorbs downstream work, so nothing is lost, merely delayed. Availability comes from decoupling, not from pretending failure is rare.
- "Why put a gateway in front at all?" — one public surface with auth pinned there, so services can move, split, or rename behind it without breaking a single client call.
- "Where do event contracts get versioned?" — consumers accept both field sets for one release cycle; producers retire shapes only after telemetry shows the last reader has moved.
- "Two teams both claim the same boundary?" — reduce it to data: whoever must touch a table to ship their roadmap owns the boundary behind that table.

---

## Closing Exchange

**Interviewer**: "Sum up the discipline in one sentence."

**Candidate**: "Every cut costs on-call duty tomorrow; take one only when the seam buys an owner, a cadence, or an independent safety story."

---

## Candidate Red Flag

Proposing a database per service "because that's what you do", while unable to say who owns each table. Real boundaries follow ownership of data and change cadence — never a slogan.
