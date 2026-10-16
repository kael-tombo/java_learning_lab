# Data Pipelines - Real-World Project: Nightly batch pipeline spec
## Scenario
daily sales extracts plus reference tables versioned by date partition. Success means a reviewer can rerun the 15-data-pipelines flow from raw files to final tables without asking for missing steps.
## Design (ingest/validate/version staging, idempotent loads, schema tests, backfill replay)
Core chain runs partitions immutable once published; reloads write new versions never in-place edits.
Method set in play: ingest/validate/version staging, idempotent loads, schema tests, backfill replay.
## Execution steps
1. Land raw extracts into date-partitioned immutable staging paths.
2. Validate schema, row counts, key uniqueness before any transform.
3. Load dimensions idempotently so reruns produce identical warehouse state.
4. Test foreign-key coverage from facts to dimensions per partition.
5. Rehearse a 7-day backfill replay on a scratch schema first.
6. Publish run book with owner, retry order, and partition-retention rule.
## Pass criteria
- partition path convention documented with example for the 15-data-pipelines dossier.
- validation gate blocks bad partitions with log evidence checked against 15-data-pipelines logs.
- rerun test shows byte-identical downstream state reproduced on rerun of 15-data-pipelines steps.
- FK coverage report per partition with miss counts stored with the 15-data-pipelines artifact set.
- backfill rehearsal log attached with timings signed off inside the 15-data-pipelines review note.
## Limits of Nightly batch pipeline spec
Textbook methods only; streaming, serving, and cost tuning belong outside this 15-data-pipelines brief.
## Evidence pack carried with 15-data-pipelines
- Raw daily sales extracts plus reference tables versioned by date partition snapshot pointer plus exact row counts.
- Dated run log linking each 15-data-pipelines build decision to its output table.
- Before/after comparison table kept beside the Nightly batch pipeline spec tables.
- Rejected-rows file with rule codes for the 15-data-pipelines audit trail.
- One-page Data Pipelines glossary defining every column the Nightly batch pipeline spec emits.
## Reviewer walkthrough for Nightly batch pipeline spec
- Reviewer opens 15-data-pipelines inputs and reproduces row counts unaided.
- Reviewer traces one rejected row from quarantine back to daily sales extracts plus reference tables versioned by date partition.
- Reviewer confirms partition path convention documented with example without extra explanation.
- Reviewer closes the Data Pipelines session with two written follow-ups.
