# Feature Engineering (Time-Aware) - Real-World Project: Loan-application feature build
## Scenario
application events with timestamps, bureau pulls, prior application history. Success means a reviewer can rerun the 04-feature-engineering flow from raw files to final tables without asking for missing steps.
## Design (datetime decomposition, rolling aggregates, count features, leakage audit)
Core chain runs every rolling count uses a strict as-of cutoff; future rows never contribute.
Method set in play: datetime decomposition, rolling aggregates, count features, leakage audit.
## Execution steps
1. Decompose timestamps into tenure, hour band, weekday with holiday flag.
2. Define as-of cutoffs per application row for all history features.
3. Build 30/90-day prior-application counts respecting each cutoff.
4. Count bureau pulls per applicant inside closed-behind windows only.
5. Run leakage audit listing every feature plus latest data it observes.
6. Freeze the feature list with cutoff logic reviewed by a second reader.
## Pass criteria
- audit table lists max observation time per feature for the 04-feature-engineering dossier.
- spot check of 20 rows shows zero future-row reads checked against 04-feature-engineering logs.
- window definitions state closed-behind boundaries reproduced on rerun of 04-feature-engineering steps.
- second-reader sign-off line present with date stored with the 04-feature-engineering artifact set.
- frozen list versioned with change log signed off inside the 04-feature-engineering review note.
## Limits of Loan-application feature build
Textbook methods only; streaming, serving, and cost tuning belong outside this 04-feature-engineering brief.
## Evidence pack carried with 04-feature-engineering
- Raw application events with timestamps, bureau pulls, prior application history snapshot pointer plus exact row counts.
- Dated run log linking each 04-feature-engineering build decision to its output table.
- Before/after comparison table kept beside the Loan-application feature build tables.
- Rejected-rows file with rule codes for the 04-feature-engineering audit trail.
- One-page Feature Engineering (Time-Aware) glossary defining every column the Loan-application feature build emits.
## Reviewer walkthrough for Loan-application feature build
- Reviewer opens 04-feature-engineering inputs and reproduces row counts unaided.
- Reviewer traces one rejected row from quarantine back to application events with timestamps, bureau pulls, prior application history.
- Reviewer confirms audit table lists max observation time per feature without extra explanation.
- Reviewer closes the Feature Engineering (Time-Aware) session with two written follow-ups.
