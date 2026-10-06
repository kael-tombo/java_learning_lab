# Lab 19: Java Architect Decision Framework — Real World Project

## Scenario: "The Decision Nobody Made"

You are a principal engineer at a fintech platform: 16 Spring Boot 3 services, Java 21, Kubernetes, PostgreSQL 15, 120 engineers, 9 squads. You have been asked to "own architecture quality" — which in practice means helping with the decisions that have been made *by default* rather than by choice.

**What you find when you look for the architecture's decisions**:

The system works, but nobody can explain it:

1. **Messaging**: three services publish to a RabbitMQ cluster that a 2019 vendor recommended during a procurement cycle. The vendor relationship ended two years ago; the cluster is a single-AZ instance type, unpatched at one CVE, and two engineers on the team have ever seen it configured. Nobody owns it. There is no ADR.
2. **The monolith that grew**: `payments-core` is 340,000 lines and handles card capture, refunds, settlement, and statement generation. It came from two acquisitions. Nobody decided to make it this way; two teams merged into one codebase and both kept adding to it.
3. **Sharding that was never sharded**: `orders` was partitioned by hash *in application code* in 2021, at 4% of current volume. Now at 380M rows, every query that needs two keys does a scatter-gather across 64 logical shards. Nobody remembers why 64.
4. **The retry policy copied from a blog post**: no service has a retry budget; the `payments-core` retry loop retries three times with no backoff cap. It has caused two incidents.
5. **No SLOs anywhere**: monitoring is alerts-only, and the on-call rotation receives 14 pages per shift.
6. **What people actually want**: the CTO wants a rewrite plan. Squad leads want to be left alone. Engineering wants to know whether they will be fired in a reorg. Nobody has asked for an architecture review.

**The trap**: the obvious response — a grand redesign — would be the wrong decision, and it would be made without a context, without options, and without anyone who will live with it.

**Your job over 4 weeks**: run architecture decisions the way they should have been run. Find the implicit decisions, reconstruct their context, evaluate options with arithmetic, produce ADRs, and present one decision to the CTO with an explicit ask. Do not redesign anything.

**Time**: 30–40 hours | **Difficulty**: Advanced

---

## Phase 1 — Find the implicit decisions (Day 1–4)

### 1.1 Decision archaeology

For each of the six situations above, reconstruct what was decided, when, by whom (if determinable), and what the forces were at the time. Use git history, PR discussions, architecture docs, ADRs (there is one, for the 2019 messaging decision), and interviews with people who were there.

**Deliverable 1 — Archaeology** per decision: the decision, the date, the decider (or "no explicit decider"), the forces at the time, and the evidence. Flag every decision with no decider as decision debt.

### 1.2 Door classification and diligence sizing

Classify each decision as two-way or one-way, and size the diligence that would have been appropriate:

| Decision | Door | Diligence that was warranted | What actually happened |
|---|---|---|---|
| Messaging (2019) | One-way (protocol + vendor lock) | Weeks: TCO over 5 years, exit plan, compliance review | A procurement default |
| `payments-core` merge | One-way (people + code) | Months: modularisation plan before merging | Two repos merged |
| 64-way hash sharding (2021) | One-way (data layout) | Weeks: capacity model, rebalancing design, query-pattern analysis | Copied from an internal template |
| Retry policy | Two-way | Days | Blog post |
| No SLOs | Two-way | Weeks | Never attempted |

**Deliverable 2 — Door classification** with the diligence table, and a blunt statement of which decisions could most plausibly be revisited *now* versus which are locked in.

### 1.3 Cost of the status quo

Quantify the six situations: broker operating cost and risk exposure, the monolith's change-cost, the scatter-gather query cost, the retry amplification cost, the alert load, and the on-call hours. Use the arithmetic from Labs 06, 14, 15, and 16.

**Deliverable 3 — Status-quo cost**, with the numbers and an expected-annual-loss figure per item, so the comparison against any change is possible.

### 1.4 Decision-debt register

Every implicit decision, with: owner (or "none"), reversibility, cost, risk, and whether it should become an ADR now.

**Deliverable 4 — Decision-debt register** — the source of truth for the rest of the work.

---

## Phase 2 — Write the missing records (Day 4–8)

### 2.1 Reconstruct ADRs for the locked-in decisions

For the four one-way decisions, write a *retrospective ADR* that reconstructs the context and records the decision as it stands today. These are explicitly labelled "retrospective: the decision was made without a record; this captures the current state and its consequences."

**Deliverable 5 — Four retrospective ADRs** (messaging, `payments-core`, 64-way sharding, retry policy), each with context, decision-as-is, consequences including negatives, and a revisit trigger.

### 2.2 Forward ADRs for the reversible gaps

For the reversible decisions (SLOs, alert quality, retry budgets, feature-flag policy), write forward ADRs making the decision properly.

**Deliverable 6 — Forward ADRs** for the four reversible gaps, each with alternatives, negative consequences, and triggers.

### 2.3 Test the ADRs

Give each to an engineer who did not work on the reconstruction, without the archaeology document. Ask: what was decided, what was given up, what would make you revisit it?

**Deliverable 7 — Comprehension results**. Rewrite any ADR that fails.

---

## Phase 3 — Decide the one decision that matters (Week 2)

Choose the messaging decision — it is the highest expected annual loss, the largest single-team-risk concentration, and the most tractable.

### 3.1 Options

- **A**: Stay on RabbitMQ — remediate it properly (multi-AZ, patch, monitoring, runbook, ownership) and accept the vendor-protocol coupling.
- **B**: Migrate to a managed cloud queue (fully managed, standard protocols, moderate vendor coupling).
- **C**: Migrate to a log-based backbone (Kafka-compatible) — highest capability, highest operational cost, largest migration.
- **D**: Consolidate into PostgreSQL outbox + logical decoding (fewest new systems, limited scale and fan-out, and it makes the database a critical path for messaging).
- **E**: No decision — cost it explicitly.

### 3.2 Quantify

Three-year TCO per option, including: infrastructure, licences, migration effort, ongoing maintenance FTE, exit cost, and opportunity cost. Plus expected annual loss from the risk profile (single-AZ, unpatched, two-person knowledge).

```markdown
| Term | A (stay) | B (managed queue) | C (log backbone) | D (outbox+CDC) | E (no decision) |
|---|---|---|---|---|---|
| Infra/yr | | | | | |
| Build | | | | | |
| Migration | | | | | |
| Maintenance FTE | | | | | |
| Exit cost | | | | | |
| Opportunity cost | | | | | |
| EAL | | | | | |
| **3-year total** | | | | | |
| **Variance** | | | | | |
```

### 3.3 Value of information

What would change the answer? Specifically: what would an incident-free operation of RabbitMQ for another 12 months do to the EAL? What would a 4-week spike on one candidate tell you that the model cannot?

**Deliverable 8 — Decision analysis** with the TCO table, the variance statement, the value-of-information analysis, and an explicit recommendation.

### 3.4 Consult and decide

Consult: the platform team that will own it, the squads that publish to it, the on-call rotation, security (the unpatched CVE), and finance. Record what changed as a result.

**Deliverable 9 — Consultation record** and the decision, with the decider named and the date.

---

## Phase 4 — Present it (Week 2)

One page to the CTO. Not a redesign — a decision with an ask.

```markdown
# Decision needed: the messaging backbone

**By when**: <date> — the unpatched vulnerability's support window closes <date>
**Who decides**: CTO (budget) with the VP Engineering (risk acceptance)

## The situation in one paragraph
<the numbers: 3 services depend on it, single-AZ, one unpatched CVE, two people
know it, $X/yr to run, expected annual loss $Y>

## Options
<4 options + do nothing, with 3-year cost and risk>

## Recommendation
<option> — <one-sentence reason with the number>

**What we give up**: <negative consequence in business terms>

**The ask**: <engineer-months>, <budget>, decision by <date>

**If we do nothing**: <concrete consequence, with date and cost>

**Confidence**: <expected-value range; worst case; what would change our mind>
```

Handle the reorg anxiety directly and honestly in the meeting: the ask is framed as "make one recorded decision and reduce one concentration of risk", not "replace the platform". Say it out loud; leaving it unsaid is what makes architecture conversations political.

**Deliverable 10 — Executive memo** plus a record of the questions asked and the decision made.

---

## Phase 5 — Handle the redesign temptation (Week 3)

The CTO's ask is a rewrite plan for `payments-core`. Do not write one. Instead:

1. Write an ADR on whether to modularise `payments-core`, with options: modularise in place (extract by domain, enforce boundaries with ArchUnit), extract services for the two domains that genuinely need independent scaling or ownership, do nothing, or rewrite.
2. Quantify: the change-cost of the monolith (`change_frequency × cost_per_change`), the migration cost of each option, and the opportunity cost.
3. Recommend the cheapest option that removes the actual pain (change cost), and name what you are explicitly not fixing.
4. Apply the **debt interest** rule (Lab 19 MATH §9): pay down where change happens, via "leave the seam cleaner", not via a dedicated rewrite team.

**Deliverable 11 — `payments-core` ADR** with the quantification and a recommendation that is almost certainly *not* a rewrite, with the arithmetic that shows why.

---

## Phase 6 — Fix the cheap, high-value things now (Week 3)

Do not wait for the messaging decision to improve these:

1. **Retry budgets**: cap global retries at 10%, add backoff caps, remove retries from non-idempotent operations, alert on retry ratio. Measure the incident-cost saving.
2. **SLOs**: define availability and latency SLIs for the top 10 services, with error budgets. Convert the 14 pages/shift into burn-rate alerts plus tickets, and measure the reduction.
3. **Alert quality**: the audit and deletion exercise from Lab 14, run across the whole estate.
4. **The scatter-gather query**: measure the cost of the 64-way hash sharding on real queries, and write an ADR on whether to reduce the shard count (a one-way door — so this is an ADR, not a change).

**Deliverable 12 — Quick wins** with before/after measurements: retry ratio, pages per shift, actionability fraction, and the measured cost of the scatter-gather queries.

---

## Phase 7 — Governance and the habit (Week 3–4)

- **ADR process**: template, required fields, storage, trigger checks.
- **Index**: every decision in one file, with statuses.
- **Decision review**: a quarterly 60-minute session that reads the index, checks fired triggers, and makes at most two decisions.
- **Design review**: any decision meeting the "expensive to reverse, cross-team" bar requires one ADR in the same PR.
- **Teach-back**: run the ADR comprehension test with three engineers as a training exercise.

**Deliverable 13 — Governance** with the process, the live index, the first decision review held, and the comprehension-test results.

---

## Phase 8 — Quantify and report (Week 4)

| Metric | Before | After |
|---|---|---|
| Architecture decisions with an ADR | 1 (2019) | 12 |
| Decisions with an explicit decider | 1 | 12 |
| Decision debt items in the register | 6 | 6 recorded, 4 closed |
| Highest expected annual loss | $X/yr (broker) | $Y/yr after the decision |
| Concentrations of unowned critical infrastructure | 3 | 0 |
| Retry amplification incidents (12 mo) | 2 | 0 |
| Pages per shift | 14 | ≤ 3 actionable |
| Services with an SLO | 0 | 10 |
| `payments-core` change cost | +6 h/change | tracked, with a paydown rule |
| Decision review cadence | none | quarterly, held |
| Engineers who have written an ADR | 1 | 8 |
| Scenario: "can a new engineer explain why we use X?" | no | yes, tested |

Present this with an honest framing: the value is not the twelve ADRs, it is that **the next six decisions will be made deliberately instead of by default** — and the one incident that dominates your expected annual loss now has a decision attached to it.

**Deliverable 14 — Business case + institutionalization**, including the CTO's decision and the follow-up commitment.

---

## Deliverables checklist

- [ ] Phase 1 archaeology, door classification, status-quo cost with EAL, decision-debt register.
- [ ] Phase 2 four retrospective ADRs, four forward ADRs, comprehension results.
- [ ] Phase 3 decision analysis (TCO, variance, EVPI), consultation record, decision.
- [ ] Phase 4 executive memo and the decision made.
- [ ] Phase 5 `payments-core` ADR quantifying why not to rewrite.
- [ ] Phase 6 quick wins with before/after measurements.
- [ ] Phase 7 governance, index, first decision review, comprehension training.
- [ ] Phase 8 before/after business case.

---

## Rubric

| Dimension | Weak | Strong |
|---|---|---|
| Archaeology | "The broker is old" | Decision, date, decider, forces at the time, evidence; "no decider" flagged as debt |
| Door classification | "Some are reversible" | One-way vs two-way with warranted diligence vs what happened, and which are revisitable now |
| Status-quo cost | "It costs a lot" | Per-item expected annual loss with the arithmetic from Labs 06/14/15/16 |
| ADRs | "We wrote them up" | Reconstructed context, negative consequences, observable triggers, comprehension-tested |
| Quantification | "Managed is cheaper" | Three-year TCO with exit and opportunity cost, EAL, and a *variance* statement |
| Value of information | "We should test more" | What would change the answer, whether the spike costs less than the decision |
| Executive memo | "We need to replace the broker" | One page, options, do-nothing priced, explicit ask, confidence range, reorg anxiety addressed |
| Restraint | "Here is the rewrite plan" | The monolith ADR recommends modularisation, not a rewrite, with the arithmetic |
| Governance | "Write ADRs" | Template, index, quarterly trigger review, PR-time requirement, comprehension training |
| Outcome | "We made 12 ADRs" | Concentrations of unowned risk closed, highest EAL addressed, decisions now deliberate |

---

## Sourced field notes (fetched Oct 2026 — verify before citing)

1. **Martin Fowler — "Microservices" and "MonolithFirst" / "MonolithModule"** — https://martinfowler.com/articles/microservices.html — the reference for two things this lab needs: the argument that "you must have a firm grasp of the boundaries before you split, and the cost of distributed systems is the absence of compile-time safety across them" (which is the quantitative case for modularising the monolith rather than rewriting or blindly splitting it), and the observation that a monolith's problems are usually solved by modularising it first, *if* it can be given strong module boundaries. Use it to support the Phase 5 recommendation with a citation rather than with preference.
2. **Architecture Decision Records — the format, and "Documenting Architecture Decisions"** — https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions — Michael Nygard's original ADR article and the canonical definition: "an architecture decision is a significant choice... recorded for future reference", with the four elements (title, context, decision, consequences) and the recommendation to keep ADRs short, numbered, and *never edited after acceptance* — supersede instead. This is the primary anchor for Phase 2 and the governance process. If your organisation has internal guidance on decision records, reconcile with it rather than replacing it.

Additional anchors worth verifying: your organisation's own architecture-review and design-review processes (and whether an ADR requirement already exists somewhere that people bypass — reconcile before adding a second process); the state of your 2019 messaging decision's vendor support window and the CVE's actual severity and exposure (confirm before using it as a forcing deadline); and the currency of the Amdahl/Little's-Law-derived change-cost model you use for the `payments-core` arithmetic — the numbers should come from your own measured `change_frequency × cost_per_change`, not from a generic figure.

---

## Reflection questions

1. Six decisions, one ADR. What is the failure mode that produces that ratio, and which single practice would most reduce it?
2. The CTO wants a rewrite plan and the honest answer is "no". How do you present a no without it being read as obstruction?
3. The 2019 messaging decision was a procurement default. What process would have caught it — a review board, a procurement gate, or an ADR requirement — and which is cheapest?
4. Six quick wins were available without any decision. Why were they not done, and what does that tell you about the incentive structure?
5. Twelve engineers have now written an ADR. What is the risk of a flood of low-value ADRs, and what quality bar prevents it?
