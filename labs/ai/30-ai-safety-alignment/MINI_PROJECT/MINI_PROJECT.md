# AI Safety & Alignment — Mini Project

**Goal**: a single-file "guard bench" that runs three safety-relevant checks over a
ratings sim: selective thresholds, proxy-gap tracking, and an escalation ledger. All
truths are typed into the source; no claim exists beyond the printed rows.

## The three modules

1. `SelectivePolicy` — reusable threshold sweep (given `score[]`, `correct[]`): emits
   coverage/accuracy rows plus one lowest-coverage row with answered accuracy at or above
   a configurable target (default 0.9). If no threshold satisfies the target, prints
   `TARGET-UNREACHABLE` and the best row instead (state this fallback in print).
2. `ProxyGapWatch` — two-column accuracy ledger per policy family (truth-first vs
   score-first) over N cases; prints per-case deltas AND total gap; flags any case where
   the two policy families disagree in their pick.
3. `EscalationLedger` — a log format of one line per incident bucket, e.g.
   `escalated | threshold=0.7 | cases=2 | reviewer-action=triage-only`; entries must
   reference the exact threshold row that put them there (traceability).

## Scenarios to run (hard-wired fixtures; clearly labeled synthetic)

- Scenario A: the snippet's five-case set as-is.
- Scenario B: 8-case set where 2 borderline rows score `0.85` but are wrong —
  deliberately placing a high-confidence falsehood; the flagged case count must grow.
- Scenario C: 8-case set of a truth-score INVERSE pairing: proxy prefers every wrong
  answer; total gap prints exactly `-8/8` and the flag list covers all cases.

## Acceptance

- `javac --release 21`, deterministic single run (no RNG at all — fixtures only).
- Ledger lines parse back through a `LedgerReader` you include (assert count of
  `escalated` lines equals the threshold-row coverage minus auto-answered).
- A five-bullet README: what each check catches, what each one misses (a systematic
  scale-miscalibration shows the SAME threshold table as honest confidence — name that),
  and an explicit note that nothing here touches a deployed model.

## Deliverable style

Output only ASCII; round to 4 dp when a fraction appears; a reviewer must be able to re-
run and match your committed stdout exactly.
