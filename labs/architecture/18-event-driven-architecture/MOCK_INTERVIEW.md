# Mock Interview: Streams, Ordering, and Rebuildable Projections

> Question-and-answer sheet. ParcelLine runs parcel tracking; every scan, dispatch, and delivery is an event, and three projections hang off one stream: a status board, an exception queue, and distance-based billing.

---

## Question Sheet

1. "Two scan events for the same parcel land on different partitions in the wrong sequence."
   Order per key is the contract: hash the parcel id to one partition so a key's history stays together, and have handlers fold events by their position within the stream rather than by arrival. Folding a scan before its pickup turns "delivered" back into "out for delivery" on the board — a visible lie that costs nothing to prevent at design time.

2. "Retries and restarts redeliver events. Dedupe where?"
   In the handler's local store: a seen-marker row whose unique key is the message id, and it commits together with the outcome in one local transaction. Redelivery without a marker means process again; with one, skip. Grace lives next to state, never three systems away.

3. "A deploy corrupts the status board. Rebuild path?"
   Build board v2 from the stream into a shadow store, compare sampled parcels old-versus-new, then flip readers when the sample agrees. Nothing in a projection is precious — the stream is the authority, any read shape is re-derivable, and that property is why bugs in views stay cheap.

4. "Streams run years long. Folding from zero at every startup?"
   Periodic snapshots of folded state give a warm start: load the snapshot, then replay only the tail. A snapshot is a cache over the log — losing or corrupting one costs replay time, never correctness.

5. "The platform markets exactly-once semantics. Do you believe it?"
   The claim describes one hop; our pipeline crosses several systems. Guarantee happens where state changes: outcome and seen-marker in a single local commit make a replayed scan touch nothing twice. Vocabulary from the broker is marketing until the handler proves it locally.

6. "Why keep the full stream once projections hold every answer?"
   Because projections only answer today's questions. The stream answers retronyms: "what did this parcel's status look like in March", debugging by replay, and new views for new enquiries without touching existing systems. Deleting history deletes the ability to be wrong safely.

7. "Can the log compact?"
   Per topic, no global rule. Billing streams never compact — totals need history. Status feeds may compact to the latest record per key, since only the newest fact matters; each projection chooses, and the choice is written down.

8. "Partition counts — fixable later?"
   Only expensively: the key-to-partition mapping sets parallelism, so it is sized against peak load at design time, and rekeying is the known, costly escape hatch rather than a plan.

---

## Probes

- "Billing projection diverges from the finance team's manual tally. First move?" — recompute from the log into a shadow projection, diff against finance's numbers, and fix the fold. Never patch a projection row in place; that hides the fold's own defect.
- "Which consumer ordering do you relax, and when?" the exception queue tolerates mild reordering because its items are independent; billing tolerates none, because totals are sums — tolerance is per projection, not a global setting.
- "How are reader positions tracked?" — each projection stores its own stream position beside its output; restarts resume from there, and only an explicit rebuild order replays from zero.
- "What about late corrections?" — a correction enters the stream keyed to the same parcel and folds by position; the board reflects it within ordinary lag, and totals recompute rather than being patched.
- "Backpressure story?" — a slow reader pulls smaller batches and parks at batch boundaries; the log retains everything meanwhile, so the consequence is delay, never loss.

---

## Red Flag

Writing events that describe present state — "status = delivered" — instead of completed facts with their own timestamps. Current-state messages cannot be replayed to rebuild anything, which quietly amputates the entire rebuild story.
