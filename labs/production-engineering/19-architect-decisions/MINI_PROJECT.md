# Lab 19: Java Architect Decision Framework — Mini Project

## Project: `DecisionLab` — Run One Real Decision Properly, From Options to ADR to Memo

**Time**: 10–14 hours | **Difficulty**: Intermediate–Advanced | **Stack**: Markdown, a spreadsheet for the TCO model, `adr-tools` or `log4brains` for the ADR toolchain, Mermaid for the context diagram, a real repository you have commit rights to

Take one genuinely pending, expensive-to-reverse decision in a team you know, and run the whole process: classify the door, enumerate options, model TCO and risk, consult, decide, write the ADR, and present it upward.

---

## Part 1 — Pick the decision

Choose a decision that is (a) real, (b) expensive to reverse, (c) cross-team, and (d) currently undecided. Candidates:

| Decision | Door type | Why it is interesting |
|---|---|---|
| Event backbone: Kafka vs managed queue vs PostgreSQL `LISTEN/NOTIFY` + outbox | One-way | Data written in a format you cannot read elsewhere |
| Sharding key for `orders` | One-way | Re-sharding requires a dual-write migration |
| AuthN/AuthZ: managed IdP vs in-house | One-way (protocol lock-in) | Vendor protocol commitment |
| Read model: CQRS projection vs direct queries | Mostly two-way | Reversible, but expensive in migration |
| Cache tier: Redis vs in-process only vs DynamoDB | Two-way | Reversible |
| Database engine migration | One-way | Data format, operational expertise |
| API versioning strategy | One-way (published contract) | External consumers you do not control |

State the chosen decision in one sentence, and name the decision-maker.

**Deliverable**: `SCOPE.md` — the decision statement, the decider, the door classification, and the date. Plus the two-way/one-way classification of five other pending decisions in your team, with a diligence plan (weeks of work) per door type.

---

## Part 2 — Context and forces

Write the context section before any option analysis. Forces to enumerate:

```markdown
## Context

### Business drivers
- Regulatory requirement: <what> by <date>
- Revenue exposure: <what happens if this is wrong>
- Product deadline: <what ships when>

### Technical constraints
- Current: PostgreSQL 15 primary + 2 replicas, 1.4 TB
- Current throughput: X rps, Y msg/s
- Current team: N engineers, M of whom have <skill>
- Existing investment: <what would be wasted>

### Organizational
- <Deadline, team structure, vendor contracts, prior commitments>
- <What is explicitly out of scope>

### Time pressure
- <Why this must be decided by DATE, and what happens if deferred>
```

**Deliverable**: `CONTEXT.md` — the context section only. Review it with two engineers who did not participate in the decision, and revise until they could explain the situation back to you accurately. That test is the acceptance criterion.

---

## Part 3 — Options

Two to four real options. For each: what it is, what it costs, what it risks, and what it makes harder later.

```markdown
## Option A — <name>
**Shape**: <one paragraph>
**Direct cost**: $X/yr
**Build effort**: N engineer-months
**Ongoing ops**: <what breaks at 3am>
**Exit cost**: <how we leave, what it costs>
**What it makes harder**: <the honest drawback>
```

Include the "no decision" option explicitly, with its cost. It is usually cheaper than people assume, and including it makes the ask legitimate.

**Deliverable**: `OPTIONS.md` — 3–4 options plus no-decision, each with the six fields above.

---

## Part 4 — Quantify

### 4.1 TCO model (spreadsheet, three-year horizon)

```markdown
| Term | Option A | Option B | Option C | No decision |
|---|---|---|---|---|
| Infrastructure /yr | | | | |
| Licences /yr | | | | |
| Build (months × rate) | | | | |
| Migration effort | | | | |
| Ongoing maintenance FTE | | | | |
| Exit cost | | | | |
| Opportunity cost of the time | | | | |
| **3-year total** | | | | |
```

Include the two terms that are usually omitted: exit cost and opportunity cost.

### 4.2 Expected annual loss

```
EAL = P(failure per year) × cost per failure
```

Derive `P` from something defensible: the incident history, the vendor's published SLA, the number of single points of failure in the design, or the results of a chaos experiment (Lab 18).

### 4.3 Expected-value comparison and the variance point

Present the mean (TCO) and the spread (EAL). Then state plainly: *two options with similar expected cost can have wildly different planning risk, and the second one is the reason roadmap commitments slip.*

### 4.4 Value of information

Before deciding, ask: what investigation would change the answer, how long would it take, and how much does it cost relative to the decision?

```
EVPI = max_E[act on Q] − max_E[act now]
```
If `EVPI > 0` and the investigation is cheaper than the decision, investigate. If it is not, decide now and be explicit about the uncertainty.

**Deliverable**: `QUANTIFICATION.md` — the TCO table, the EAL calculation, the variance statement, and the value-of-information analysis with a decision to investigate or not.

---

## Part 5 — Consult, then decide

- Present the options to the people who will live with them (the on-call rotation especially) and to whoever owns the budget.
- Record the objections; a strong objection that changes nothing should change the ADR (usually a consequence or a trigger).
- Name the decider and get an explicit decision. No silent defaults.

**Deliverable**: `CONSULTATION.md` — who was consulted, what they said, which concerns were accepted, and the explicit decision with its date.

---

## Part 6 — The ADR

`adr/0042-event-backbone-choice.md`:

```markdown
# 42. Event backbone for the platform

Date: 2026-XX-XX
Decider: <name>
Status: Accepted
Supersedes: none
Superseded by: none

## Context

<the context from CONTEXT.md, condensed to what a reader needs in 90 seconds>

Business: compliance requirement by 2026-09-01; revenue exposure $X/yr if
message loss or duplication reaches the ledger.
Technical: 45k msg/s peak, 1.4 TB, team of 9 (2 with streaming experience).
Time: must be decided by 2026-07-01 or we inherit the vendor's default for a year.

## Decision

We will use <option>, with <the specific configuration that matters>,
and we will <what we will NOT do, explicitly>.

Boundaries: producers must write to the outbox; the schema registry is the
compatibility gate; consumer groups are per-team; the broker is not exposed to
services directly (only via the outbox relay).

## Alternatives considered

**Option B — managed queue**
Rejected because: <specific reason tied to the current forces>.
Revisit if: <condition>.

**Option C — PostgreSQL LISTEN/NOTIFY + outbox**
Rejected because: <specific reason>.
Revisit if: our peak falls below 5k msg/s AND we need a 3-week simpler deployment.

**No decision**
Cost of doing nothing: <the cost>. Acceptable until <date>, after which
<consequence>.

## Consequences

Positive:
- <...>

Negative (we accept these):
- <...>
- Operational burden: a broker is a new thing to be on call for. First pager
  at 3am belongs to the platform team, named in the runbook.
- Team skill: 2 of 9 engineers have streaming experience; we budget 3 engineer-weeks
  of training in Q3.

Follow-on obligations created by this decision:
- Every producer must use the outbox (enforced by CI from ADR-0043).
- Every topic needs a schema and an owner (enforced by the registry policy).
- The platform team owns broker operations, on-call, and upgrades.

## Revisit trigger

We will revisit this decision if ANY of the following becomes true:
1. Our peak exceeds 150k msg/s (current design assumed 3× headroom on 45k).
2. Consumer lag p99 exceeds 5 minutes at peak for two consecutive months.
3. Broker operations consume more than 0.5 FTE (the point at which the team's
   attention is better spent elsewhere).
4. The compliance deadline is met and we are still paying a premium; at that point
   the exit plan below is the cheaper path.

## Exit plan

Migrating away: dual-write to the new backbone for one release, replay the
consumer groups, verify counts, cut over, decommission. Estimated cost:
4 engineer-months, 2 weeks of dual running. Owner: platform team.

## Evidence

- Quantification: <link>
- Experiment: <link, e.g. the throughput test from the mini project>
- Incident history: <link>
```

Then mark the state properly:
- Any code change touching this area must cite ADR-0042.
- When the decision changes, write ADR-00XX and set `Superseded by: ADR-00XX` on 0042 — **do not edit 0042's body**.

**Acceptance test for the ADR**: give it to an engineer who did not participate, without the context document, and ask them (a) what was decided, (b) what was given up, and (c) what would make you revisit it. If they cannot answer all three, rewrite it.

---

## Part 7 — Present it upward

One page, no technology names beyond what is unavoidable:

```markdown
# Decision needed: how we carry events between our services

**What we must decide**: [one sentence]
**By when**: [date] — because [the forcing reason]
**Who decides**: [role]

## Options

| | What it means for the business | Cost | Risk over 5 years |
|---|---|---|---|
| A | | | |
| B | | | |
| C | | | |
| Do nothing | fails <requirement> by <date>, costing $X | — | |

## Recommendation
Option A. Because <the one-sentence reason with the number>.

**What we are giving up**: <the negative consequence in business terms>.

**The ask**: 2 engineer-months of engineering time and a decision by <date>.

**If we do nothing**: <the concrete consequence and its date>.

**How confident are we**: <expected-value range, worst case, and the main risk
to the estimate>.
```

**Deliverable**: `EXECUTIVE_MEMO.md` — the one-page memo, presented to a real stakeholder if possible, with their questions recorded.

---

## Part 8 — Decision-debt audit

Find the decisions in your system that were made implicitly:

| Implicit decision | Evidence | Reversible? | Convert to |
|---|---|---|---|
| We use PostgreSQL for messaging | `LISTEN/NOTIFY` in the code | Yes | ADR + a plan |
| Every service has its own schema per table | DB inspection | Partly | ADR + consolidation |
| This one service has no SLO | no dashboard | Yes | ADR + an SLO |
| Retry policy copied from a blog post | code inspection | Yes | ADR + a budget |

**Deliverable**: `DECISION_DEBT.md` — the audit, and three of them converted into ADRs (or into explicit "no decision needed, and here is why").

---

## Part 9 — Governance

Propose the lightest thing that works:

```markdown
## ADR process (proposal)

1. **When required**: any decision that is expensive to reverse, cross-team, or
   release-crossing. Local, cheap, reversible changes do not need one.
2. **Who writes it**: the person closest to the decision. The decider is accountable.
3. **Template**: the ADR-0042 structure above. Required fields: context, decision,
   alternatives with reasons, positive AND negative consequences, revisit trigger.
4. **Process**: PR alongside the change, reviewed like code. Merged with the change,
   not before it.
5. **Storage**: `adr/NNNN-title.md` in the repository, with `adr/README.md` as an index.
6. **Trigger check**: once per quarter, scan the index for fired triggers and report.
7. **Reuse check**: any PR touching a decision must cite its ADR. If it would
   contradict one, that PR must supersede it.
```

Then actually create the index and run one trigger check.

**Deliverable**: `GOVERNANCE.md` — the proposal, the ADR index with five records, and the first trigger-check result (even if it is "no triggers fired").

---

## Acceptance Criteria

- [ ] `SCOPE.md`: one decision statement, a named decider, and a two-way/one-way classification of five pending decisions with a diligence plan.
- [ ] `CONTEXT.md` passes the comprehension test with two uninvolved engineers.
- [ ] `OPTIONS.md`: 3–4 options plus no-decision, each with cost, ops burden, exit cost, and the honest drawback.
- [ ] `QUANTIFICATION.md`: three-year TCO including exit and opportunity cost, EAL per option, the variance statement, and a value-of-information decision.
- [ ] `CONSULTATION.md`: who was consulted, what they said, what changed as a result, and the explicit decision with a date.
- [ ] ADR-0042 passes the three-question comprehension test (decided / given up / revisit trigger).
- [ ] `EXECUTIVE_MEMO.md`: one page, an explicit ask, an expected-value range, and the "do nothing" priced.
- [ ] `DECISION_DEBT.md`: an audit of implicit decisions, three converted.
- [ ] `GOVERNANCE.md`: a proposal, a live index of five ADRs, and a first trigger check.

---

## Stretch

- Run a decision review: pick an accepted ADR, check whether its triggers have fired, and either keep it, supersede it, or close it as validated. Report which, and why.
- Compare two of your options with a Monte Carlo over the uncertain inputs (growth rate, failure probability, team velocity) instead of point estimates.
- Find a decision your organisation made two years ago, reconstruct the context from the ADR (or from git if there is none), and evaluate it against today's forces. Write the resulting ADR.
- Train a team in writing ADRs by reviewing three of their drafts against the template and scoring them.
