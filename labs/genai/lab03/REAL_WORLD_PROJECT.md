# Lab 03: Prompt Engineering Patterns — Real-World Project

## Project: Production Prompt Management and Optimization Service

Design and build the system a production team uses to run prompts as versioned,
measured, gated, and safe production assets: a registry with lifecycle, a template
service, experiment and A/B infrastructure, injection and output defenses, cost
accounting, and an optimization pipeline that cannot ship a regression.

## Context

Prompts are the largest and most frequently changed component of an LLM system. They
carry policy, affect cost, and are the usual root cause of quality incidents. Managing
them like code — versioned, reviewed, gated, rollback-able — is the single highest-leverage
operational discipline in GenAI delivery.

## Sourced field notes (fetched Oct 2026 — verify before citing)

- "Large Language Models are Few-Shot Learners" (Brown et al., submitted 28 May 2020;
  rev. 22 Sep 2021) — https://arxiv.org/abs/2005.14165 — takeaway for this lab:
  in-context demonstrations are a conditioning mechanism with no gradient updates, which
  is why demonstration selection and ordering are managed as versioned assets with their
  own experiments rather than treated as fixed template text.
- "Direct Preference Optimization: Your Language Model is Secretly a Reward Model"
  (Rafailov et al., submitted 30 May 2023; v4 7 Feb 2024) —
  https://arxiv.org/abs/2305.18290 — takeaway for this lab: prompt variants are evaluated
  by paired comparison on preference data, which is why this service implements paired
  experiments with bootstrap confidence intervals rather than aggregate score
  comparisons.

## System Architecture

```
   PRODUCT TEAMS
        |
   +----v------------------------------------------------------------------+
   |  PROMPT SERVICE                                                      |
   |  template rendering | typed variables | token budgeting            |
   +----+---------------------------+------------------------------------+
        |                           |
   +----v-------------------+     +----v--------------------------------+
   |  PROMPT REGISTRY        |     |  INSTRUCTION LAYER                   |
   |  versions | owners      |     |  policy (system message, trusted)    |
   |  risk tiers | changelog |     |  context (untrusted, delimited)      |
   |  rollout | rollback     |     |  schema | question                     |
   +----+-------------------+     +----+--------------------------------+
        |                             |
   +----v-----------------------------v--------------------------------+
   |  EVALUATION & EXPERIMENT LAYER                                     |
   |  offline suite | prompt A/B (paired) | self-consistency | CoV      |
   |  judge validation | cost-per-correct tracking                       |
   +----+----------------------------------------------------------------+
        |
   +----v----------------------------------------------------------------+
   |  OPTIMIZER PIPELINE                                                 |
   |  propose mutations | validate | select | canary | promote or reject   |
   +----+----------------------------------------------------------------+
        |
   +----v----------------------------------------------------------------+
   |  DEFENSE LAYER                                                      |
   |  injection detection | output schema validation | repair | scrub   |
   |  fail-closed | audit                                                      |
   +----+----------------------------------------------------------------+
        |
   +----v----------------------------------------------------------------+
   |  OBSERVABILITY & COST                                               |
   |  per prompt version: accuracy | tokens/correct | latency | cost     |
   |  drift on prompt performance | rollback events                   |
   +---------------------------------------------------------------------+
```

## Component Specs

### 1. Prompt Registry and Lifecycle
- Immutable versions; every version has an **owner**, a **risk tier**, a changelog, and
  a template hash.
- Lifecycle: draft -> evaluated -> canary -> active -> deprecated -> deleted.
- Promotion requires a passing gate on the registered suite; the API refuses
  otherwise.
- Rollback is a single call that also invalidates and warms the render cache.
- Render cache keyed by `sha256(name + version + rendered)`; hit rate monitored.
- Deprecation: notices at promotion, at 50% traffic, and at a deadline; auto-pin at
  the deadline.
- Every prompt usage in a trace records the prompt version.

### 2. Template Service
- Typed variables with declared types and constraints (STRING n, ENUM, INT, BOOL).
- Canonical section order: system, instructions, context, schema, question. Enforced at
  render time.
- `assertNoUnfilled` — a rendered prompt containing a literal placeholder is an error,
  not output.
- Stable/v volatile split verified so prefix caching works; CI test asserts prefix
  stability across renders.
- Token budgeting with truncation order: context first, then few-shot, never schema or
  question. Every truncation is logged.

### 3. Instruction and Context Layering
- **Policy** lives in the system message. **Untrusted content** (retrieved documents,
  user text, tool output, images) is placed in the user message, wrapped in markers,
  and labelled as data.
- The renderer never concatenates untrusted text into the policy string.
- Output contract enforced downstream (schema validation), so the instruction is a
  request and validation is the control.

### 4. Evaluation and Experiments
- Offline suite per prompt family; results keyed by prompt version.
- A/B experiments: **paired** comparison on identical items, bootstrap CIs, per-category
  diff, and prompt-demonstration ordering averaged over seeds.
- Metrics: task accuracy, format validity, refusal rate, tokens/correct, latency,
  cost per correct outcome.
- Self-consistency for high-stakes prompts, with the agreement rate reported.
- Chain-of-verification for grounded prompts, flagging unsupported claims.
- Judge validation: periodic judge-human agreement; judge metrics suspended below
  threshold.

### 5. Optimizer Pipeline
```
propose -> validate on held-out set -> canary -> promote or reject
```
- Mutations: instruction verb changes, section reordering, added counter-example,
  added step-by-step line, concision/expansion, schema restatement.
- Held-out validation set never used for tuning decisions; a separate test set for the
  final check.
- Strict acceptance (never accept a non-improvement); patience-based stopping.
- Guard against length-driven wins: report tokens/correct alongside accuracy.
- Every candidate gated by the offline suite and canaried in production before
  promotion; rejections recorded so the same idea is not re-proposed.

### 6. Defense Layer
- **Input**: injection detection (role markers, encoding decode with depth limit,
  instruction-collision heuristics) as a cheap tripwire; policy and capability still
  enforced in code.
- **Output**: schema validation with repair (bounded) and deterministic fallback;
  PII scrubbing; citation validation.
- Fail-closed: if the validator cannot decide, block.
- Per-prompt risk tier determines how strict the output layer is (e.g. financial
  prompts require schema validity; casual prompts do not).

### 7. Observability and Cost
- Per prompt version: accuracy (sampled), format validity (100%), refusal (100%),
  tokens/correct, cost per correct outcome, latency percentiles.
- Alerts: format validity drop, refusal spike, cost per correct rising, a prompt
  version with no recent eval.
- Drift: if prompt performance declines while the model is unchanged, investigate
  input drift first (intent mix, length).

### 8. Governance
- Prompt ownership is required; orphaned prompts are deprecated automatically.
- Risk tiers drive required gates: high-risk prompts (financial, legal, safety,
  PII-handling) need review plus the safety suite.
- Change control: prompt changes use the same release process as code, with the
  manifest hash shared with the Lab 14 platform.

## Non-Functional Targets

| Metric | Target |
|--------|--------|
| Prompts with an owner | 100% |
| Format validity (structured prompts) | >= 99% |
| Repair attempt rate | <= 2% |
| Fallback rate | <= 0.1% |
| Unfilled placeholders in production | 0 |
| Injection fixture detection | 100% on the internal suite |
| A/B experiments with paired CIs | 100% |
| Prompt promotion blocked on a failing gate | 100% |
| Rollback time | < 1 min |
| Cost per correct outcome | Tracked per prompt version |
| Oracle: unsafe prompt shipped | 0 |

## Failure Modes and Mitigations

| Failure | Detection | Mitigation |
|---------|-----------|------------|
| Prompt tweak ships ungated | Registry audit | API refuses promotion without a gate |
| Literal placeholder in a prompt | Render-time assertion | Throw, alert |
| Cache always missing | Prefix stability test | Volatile content out of the prefix |
| A/B concludes on noise | Paired CIs | Require CI excluding zero |
| Optimizer overfits the validator | Held-out test set | Never tune on the test set |
| Optimizer wins by being longer | tokens/correct metric | Report both; require quality per cost |
| Injection slips through | Canary suite | Code-level privilege separation |
| Output malformed in production | Format validity metric | Schema + repair + fallback |
| Refusal spike after a prompt change | Refusal metric | Alert and rollback |
| Prompt sprawl | Coverage metric | Unversioned prompts blocked in CI |
| Over-truncation drops the schema | Truncation log | Priority order enforced |
| Cost grows with quality flat | Cost per correct | Route or compress instead |
| High-risk prompt with no safety suite | Risk tier audit | Gate by risk tier |
| Nobody owns a prompt | Orphan report | Auto-deprecate orphans |

## Milestones

- **M1** — registry with owners, risk tiers, gated promotion, one-call rollback.
- **M2** — template service with typed variables, ordering, budget enforcement.
- **M3** — instruction layering: policy in system, untrusted data delimited.
- **M4** — evaluation service with paired A/B and per-category diffs.
- **M5** — judge validation and self-consistency integration.
- **M6** — optimizer pipeline with canary and rejection recording.
- **M7** — defense layer: injection detection, schema validation, repair, scrub.
- **M8** — observability per prompt version; alerts.
- **M9** — deprecation process exercised on one prompt family.
- **M10** — game day: inject a placeholder bug and an injection payload; verify both
      are caught before serving.

## Deliverables

1. Prompt registry and template service.
2. Evaluation and experiment infrastructure.
3. Optimizer pipeline with gates.
4. Defense layer implementation.
5. Dashboards and alerts per prompt version.
6. `REPORT.md` — prompt inventory by owner and risk tier, experiment results, quality
   per version, cost per correct outcome, and a list of rejected optimizations.
7. `PROMPT_STYLE.md` — the conventions, enforced by the linter.

## Definition of Done

- [ ] 100% of production prompts have an owner and a risk tier.
- [ ] Unfilled placeholders impossible in production (assertion enforced).
- [ ] A failing gate blocks promotion; verified by a deliberate regression.
- [ ] Injection fixtures 100% detected; two live payloads caught in the game day.
- [ ] Rollback under 1 minute.
- [ ] Every A/B reported with paired CIs; "within noise" written where true.
- [ ] Optimizer gains confirmed on a held-out set across multiple seeds.
- [ ] Cost per correct outcome tracked and improving per prompt family.