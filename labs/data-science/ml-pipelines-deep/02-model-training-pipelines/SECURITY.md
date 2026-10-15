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
The config hash (-1652323048 for the demo string) illustrates the
integrity-pointer idea: any change in code, params, or data reference
changes the hash and breaks silent substitution. Real systems use
cryptographic hashes; the role is identical.
