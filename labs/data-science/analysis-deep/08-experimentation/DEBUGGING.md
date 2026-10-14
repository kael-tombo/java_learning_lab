# Debugging - Experimentation

## 1. p-values that disagree with hand math

Cause: swapped arms or counts vs rates confusion (passing 0.12 where
1200/10000 belongs). Fix: assert AbTest's exact outputs on its inputs
first; any digit off means a formula transcription bug.

## 2. SRM flags on a healthy test

Cause: planned ratio was 90/10 ramp but check assumed 50/50. Fix: pass
the planned ratio into SrmCheck - expected counts derive from the
actual plan, never a hardcoded half.

## 3. CI includes 0 but p < 0.05 (or reverse)

Cause: mixing pooled-SE test with unpooled-SE interval (or z vs t).
Fix: one SE definition end to end; this lab uses unpooled everywhere -
verify both from the same Readout object.

## 4. Effect evaporates after launch

Cause: novelty/holiday/peer-review traffic mix changed. Fix: compare
launch cohort composition with test composition; segment veterans; next
time horizon past the spike.

## 5. Guardrail flat but users complain

Cause: guardrail too coarse (mean latency hides p99 pain). Fix: add
tail metrics (p95/p99, crash-free sessions) as first-class guardrails.

## 6. Segments contradict the overall

Cause: Simpson-style mix shift or multiplicity trawling. Fix: check arm
mix per segment, then treat slice wins as next-test hypotheses.

## 7. Non-reproducible readout

Cause: analysis on shifting tables (late-arriving events). Fix: freeze
the event window in the Log row; late data goes to a stated refresh,
not a silent overwrite.

## 8. MDE shrinks after launch

Symptom: planning MDE 0.02, observed SE implies 0.008. Cause: planning
rate guessed high (SE follows sqrt(p(1-p))). Fix: replan from observed
base rate for the next test; never resize the current one mid-flight.
