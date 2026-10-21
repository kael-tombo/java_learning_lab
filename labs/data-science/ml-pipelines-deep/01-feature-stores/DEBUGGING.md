# Feature Stores — Debugging

## Symptom: offline metrics look great, production flops
Likely future leakage in the training join. Check: rebuild one
training row by hand with the as-of rule and compare against the
pipeline's value. In the demo, the leaked row reads 3.0 where the
correct value is 2.0. Fix: enforce the ts <= t predicate in the join
and add a test with a label placed between two feature timestamps.

## Symptom: per-feature maxdiff alarm fires after a deploy
Likely a transform change reached one path only. Check: diff the code
hash pinned by training against the code hash deployed for serving.
In the demo, a dropped +1.0 shift shows as maxdiff 1.0. Fix: point
serving at the same registry version, redeploy, and confirm maxdiff
returns to 0.0 before trusting new metrics.

## Symptom: sudden coverage drop on a served feature
Likely an upstream delay or an over-aggressive TTL. Check: plot row
ages at serving time against the TTL. In the demo at TTL 30, half the
rows drop (coverage 0.5). Fix: distinguish late data (page the owner,
backfill the gap) from correct expiry (widen TTL deliberately or accept
the missing rate with proper imputation).

## Symptom: entity has no features at serving time
Likely a new entity with no history, or a materializer lag. Check:
query the offline log for that entity; if rows exist offline but not
online, the materializer is behind. If no rows exist anywhere, the
entity is genuinely new. Fix: lag gets a materializer restart from the
last checkpoint; new entities get the declared cold-start default.

## Symptom: backfill changed old model behavior
Likely the old model was repointed at a new version. Check the serving
config's version set. Fix: pin models to immutable versions; rollback
is repointing to the previous version, never editing rows.

## Debugging checklist
1. Reproduce one row by hand (as-of rule).
2. Compare code hashes train vs serve.
3. Compare age histograms vs TTL.
4. Check materializer lag vs genuinely new entities.
5. Confirm version pins before and after the incident.
