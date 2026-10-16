# MLOps Orchestration - Security

## Secrets
- Inject credentials per run from a secret service; never bake them into images.
- Scope tokens to the run and expire them after completion.
- Audit every promotion with author, lineage pointer, and timestamp.

## Isolation
- Run untrusted steps (new data parsers) with minimal filesystem and network scope.
- Separate training, staging, and production artifact namespaces.
- Require review for DAG changes that touch promotion or traffic.

## Reproducibility as control
- Pinned dependencies and recorded commits make tampering detectable.
- Verify artifact hashes at each stage against the run record.
- Backfill writes go to versioned paths; never overwrite live data in place.

## Access
- Least-privilege roles: trigger, edit, approve-promotion, and read-audit stay separate.

## Promotion authority
- Require second approval for production promotion; staging stays single-approver.
- Record approver identity with the lineage pointer in the promotion record.
- Emergency promotions expire: re-gate within one cycle or roll back.

## Artifact signing
- Sign datasets, models, and evaluation sets at write time.
- Verify signatures at stage boundaries, not only at final promotion.
- Reject unsigned artifacts before expensive training starts.

## DAG change control
- Promotion-touching DAG edits need review from the model owner.
- Test DAG changes on one backfill window before full scheduling.
- Keep prior DAG versions runnable for in-flight runs during migration.

## Secret scoping
- Mint per-run credentials with the narrowest partition and artifact scope.
- Expire tokens at run completion; audit any use after expiry as an incident.
- Never log secret values; log issuance, scope, and expiry only.

## Data governance
- Track dataset licenses and consent boundaries as lineage metadata.
- Block training on partitions whose governance flags changed since pinning.
- Quarantine suspect data the way poison partitions quarantine bad rows.
