# Mock Interview: Strangling a Legacy Portal, One Route at a Time

> Transcript with probes. PosterHive, a print-on-demand storefront whose core is a ten-year-old monolith deployed monthly. Break-glass changes are the norm; a two-year migration is on the table.

---

## Warm-Up

"Pick the first slice. Defend it."

"The order-history page: a read path, modest traffic, no money movement. The opening slice is a rehearsal for the routing machinery itself — it should be reversible in minutes and give the team confidence in the seams before a revenue path is touched."

**Interviewer**: "How does traffic actually arrive there?"

**Me**: "An edge router matches the path prefix plus a per-customer toggle. Matched requests reach the new service; everything else keeps hitting the monolith. Default stays legacy, and new code wins share only on evidence — opt-in cohorts first, then widen by percentage."

**Interviewer**: "The new service needs order rows it cannot write yet."

**Me**: "During this phase the new service reads a batch-copied dataset refreshed hourly, while the monolith remains the only writer. Dual-write waits for the later write-phase slice, and even then the monolith stays authoritative; a nightly job diffs both stores row by row and alarms on mismatch."

**Interviewer**: "And the rollback story?"

**Me**: "Flip the routing rule off; traffic lands back on the monolith in seconds. We rehearse every flip in staging before any real cohort sees the slice, so rollback is one flag — never a convened war room."

**Interviewer**: "When is a slice actually done?"

**Me**: "Two clean weeks at full cohort traffic, error rate inside the agreed budget, zero unexplained diffs — and then the monolith's code for that page is deleted. Retirement is removal; a route that merely stops being served still ages."

**Interviewer**: "Two years is long. What sustains momentum?"

**Me**: "Shipping cadence: a slice or a widening every few weeks, however small. Momentum is a property of the plan, and plans with no visible increments die quietly halfway through."

**Interviewer**: "The monolith keeps evolving mid-migration. Deal with it."

**Me**: "The strangling contract: new features for a transferred area are built only in the new service, while the monolith receives fixes for what remains ours. Without that rule the target keeps moving and the fig never covers the trunk."

**Interviewer**: "How does the whole thing end?"

**Me**: "The router's legacy bucket stays empty for a full release cycle, then the monolith is switched off and the routing layer retires to plain forwarding. Nobody celebrates a cutover night; the win is that there wasn't one."

---

## Probes the Panel Runs

- "What breaks your sequence?" — a write-heavy slice nobody copied correctly, or a data contract the legacy schema makes implicit. Both call for a longer shadow phase, not more courage.
- "How do you prove correctness page by page?" — parallel-run comparisons on the read path during opt-in, sampled nightly, with discrepancies triaged before widening.
- "Toggle cleanup?" — every routing toggle carries an expiry; one that outlives its slice's graduation becomes a tracked item, because stale toggles rot routes into permanent ambiguity.
- "What stays legacy longest?" — the billing write path, by choice: money and history concentrate there, so it moves last and gets its own full rehearsal cycle.
- "Parallel-run forever?" — no: comparisons end when a slice graduates. Two clean weeks, then that slice's diff job is retired with it; permanent parallel running is a tax without a payoff.

---

## Candidate Red Flag

A "strangler plan" whose slice one requires half a year of platform prerequisites. That is a big-bang rewrite wearing incremental vocabulary, and the tell is that nothing user-visible ships in quarter one.
