# Feature Stores — Security

## Threats specific to feature layers
- Poisoned history: a writer pushes crafted values that later train
  models. Mitigate with authenticated writers and append-only logs.
- Version confusion: serving resolves the wrong version and leaks a
  future or experimental definition. Mitigate by pinning version sets
  in serving config, not "latest".
- Entity leakage across tenants: a lookup returns another tenant's
  vector. Mitigate with tenant-scoped keys and access checks at read.

## Controls
- Write ACLs per feature; only the owning pipeline may append.
- Signed lineage: dataset receipts include code+data hashes so
  tampering is detectable.
- PII minimization: store derived features, not raw identifiers, where
  possible; encrypt at rest; audit reads of sensitive entities.

## What this lab demonstrates
The TTL snippet shows expiry as a correctness control that doubles as
a staleness bound. The versioning exercise shows pinning as the
rollback and isolation mechanism. Both are security-relevant because
both limit the blast radius of a bad write.

## Incident walkthrough: suspected poisoned feature
1. Freeze: pin serving to the last known-good version; do not delete
   rows (append-only log preserves evidence).
2. Scope: query the lineage DB for every dataset and model built from
   the suspect version range.
3. Diff: recompute expected vectors from the offline log with the
   pinned transform and compare per-entity against served logs; the
   maxdiff per feature bounds the exposure.
4. Remediate: backfill a corrected version, revalidate, retrain
   affected models, and rotate writer credentials if the write was
   unauthorized. Record all four steps in the incident log.
