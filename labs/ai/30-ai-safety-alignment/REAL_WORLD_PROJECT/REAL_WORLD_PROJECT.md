# AI Safety & Alignment — Real-World Project

**Goal**: design a review-and-abstain flow for an automated assistant inside a company
data terminal — Java-side orchestration concepts with a visible audit trail. All examples
are self-written; no workplace data is ingested.

## The flow to design (and prototype the ledger)

1. A classifier (stubbed as `ScoreProvider` returning a quality score + category tag)
   screens every generated answer on its way to a user.
2. Answers scoring below the auto-answer threshold escalate to reviewer triage; answers
   in an ambiguous band get flagged for sampling-based audit.
3. A `FeedbackLoopStub` records reviewer outcomes; the design memo explains what retraining
   on that feedback must guard against.

## Prototype pieces to build

- `ScoreProviderStub`: 12 hand-typed cases covering on-topic/wrong/correct categories
  (a table, exactly like the two deep-dive snippets').
- `AbstainRouter`: thresholds `(autoAnswer = 0.9, flagBand = [0.6, 0.9))` from config;
  emits a routing case per case (auto/flag/review) plus a queue-length counter.
- `AuditTrail`: append-only log (in-memory) of each decision with category, score, and
  policy version constant; supports a `replay()` that reprints decisions from the log.
- `BiasProbe`: category-conditional routing rates with a check — flagBand must NOT
  concentrate categories; print per-category routing table and name the guard you'd add
  if concentration appears.

## Required write-up (where candor earns marks)

- Limits: score stubs are guesses; real score drift, calibration loss under distribution
  change, and adversarial prompts are all untested here — one bullet each, no specifics
  claimed about deployed systems.
- The retraining trap: reviewer feedback is filtered through the very thresholds you set;
  state that the feedback pipeline sees mostly medium-confidence items and what that skews.
- Escalation economics: from your routing table, compute triage hours vs auto-share at
  two threshold settings — a trade-off you present to stakeholders with both numbers
  visible rather than one recommended silently.

## Constraints

`javac --release 21`; single file; deterministic; stdout ASCII-only with a fixed-width
log; include a `README` block noting nothing here constitutes a production policy.
