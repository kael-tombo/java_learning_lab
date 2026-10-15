# Model Training Pipelines — Security

## Threats specific to training pipelines
- Data poisoning: crafted rows in the source become model behavior.
  Mitigate with authenticated ingest, versioned snapshots, and
  validation bounds that reject anomalous batches.
- Code substitution: unreviewed transform or trainer code ships a
  backdoored model. Mitigate by hashing tracked code and requiring
  reviewed commits for registered versions.
- Registry tampering: a promoted artifact is swapped post-hoc.
  Mitigate with immutable blobs plus signed promotion records.
- Secret leakage: credentials or PII baked into artifacts or logs.
  Mitigate by redacting secrets from tracked params and scanning
  artifacts before registration.

## Controls
- Write ACLs: only the pipeline identity may write dataset versions
  and register models; humans get read plus explicit promotion rights.
- Provenance on every artifact: code hash plus data hash, checked at
  promotion time against allow-lists.
- Audit trail: every stage transition (pass/fail/retry/promote) logged
  with actor and timestamp.

## Demo connection
This lab's DAG demo chains each stage's artifact hash into the next
(head `9a545d0` for the six-stage run) — the same integrity-pointer
idea: any change in an upstream artifact changes every downstream hash
and breaks silent substitution. Real systems use cryptographic hashes
over the artifact bytes; the role is identical.

## Least privilege for schedulers
Pipeline runners need write access to exactly one staging area plus
append-only logs; promotion to production registries goes through a
separate approval identity. A compromised training job then cannot
promote itself, and a compromised notebook cannot rewrite history.
