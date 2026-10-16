# Data Wrangling - Real-World Project: Municipal service-request cleaning pipeline
## Problem
311-style request extracts with inconsistent spellings, null wards, duplicated ticket ids. Success means a reviewer can rerun the 01-data-wrangling flow from raw files to final tables without asking for missing steps.
## Architecture (schema validation, missing-value treatment, record dedup keys, tidy reshape)
Core chain runs quarantine report counts rows rejected per rule; dedup keeps earliest ticket id; reshape one row per request-event.
Method set in play: schema validation, missing-value treatment, record dedup keys, tidy reshape.
## Build sequence
1. Profile every column for type, null rate, cardinality before changing anything.
2. Freeze a schema contract listing allowed ward names, date bounds, ticket-id pattern.
3. Route null/invalid rows to quarantine with rule codes instead of silent deletes.
4. Normalize text keys with trim, case folding, alias map kept in versioned CSV.
5. Dedup on ticket id plus timestamp tolerance, retaining earliest record with log.
6. Reshape wide status columns into one row per request-event tidy table.
7. Re-run profiler and diff before/after null rates, duplicate counts, row totals.
## Acceptance checks
- contract rejects 100% of out-of-vocabulary ward names with codes for the 01-data-wrangling dossier.
- quarantine log reconciles to row counts within exact integer match checked against 01-data-wrangling logs.
- zero duplicate ticket ids remain under exact-match check reproduced on rerun of 01-data-wrangling steps.
- profiler rerun shows null-rate delta documented per column stored with the 01-data-wrangling artifact set.
- tidy table passes one-row-per-request-event uniqueness test signed off inside the 01-data-wrangling review note.
## Limits of Municipal service-request cleaning pipeline
Textbook methods only; streaming, serving, and cost tuning belong outside this 01-data-wrangling brief.
## Evidence pack carried with 01-data-wrangling
- Raw 311-style request extracts with inconsistent spellings, null wards, duplicated ticket ids snapshot pointer plus exact row counts.
- Dated run log linking each 01-data-wrangling build decision to its output table.
- Before/after comparison table kept beside the Municipal service-request cleaning pipeline tables.
- Rejected-rows file with rule codes for the 01-data-wrangling audit trail.
- One-page Data Wrangling glossary defining every column the Municipal service-request cleaning pipeline emits.
## Reviewer walkthrough for Municipal service-request cleaning pipeline
- Reviewer opens 01-data-wrangling inputs and reproduces row counts unaided.
- Reviewer traces one rejected row from quarantine back to 311-style request extracts with inconsistent spellings, null wards, duplicated ticket ids.
- Reviewer confirms contract rejects 100% of out-of-vocabulary ward names with codes without extra explanation.
- Reviewer closes the Data Wrangling session with two written follow-ups.
