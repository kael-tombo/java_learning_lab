# Feature Engineering (Tabular Codes) - Real-World Project: Churn feature slice
## Brief
subscriber records with plan tier, tenure months, support contacts, monthly spend. Success means a reviewer can rerun the 03-feature-engineering flow from raw files to final tables without asking for missing steps.
## Components (one-hot and target encoding, scaling, binning, interaction terms)
Core chain runs encodings fit on training folds only; target means smoothed with prior weight.
Method set in play: one-hot and target encoding, scaling, binning, interaction terms.
## Work plan
1. Split rows into train and holdout before computing any encoding.
2. One-hot low-cardinality tier with explicit unknown-level handling.
3. Target-encode high-cardinality region ids with smoothing prior on train folds.
4. Scale spend with median/IQR scaler whose center comes from train only.
5. Bin tenure into documented bands and keep raw tenure alongside.
6. Add tenure-times-contacts interaction with written rationale.
7. Re-apply frozen transformers to holdout and log unseen-level counts.
## Done when
- no encoding statistics leak from holdout into train for the 03-feature-engineering dossier.
- smoothing weight value recorded for target means checked against 03-feature-engineering logs.
- unseen-level policy demonstrated on holdout reproduced on rerun of 03-feature-engineering steps.
- scaler center and spread values stored with provenance stored with the 03-feature-engineering artifact set.
- interaction term justified in one paragraph signed off inside the 03-feature-engineering review note.
## Limits of Churn feature slice
Textbook methods only; streaming, serving, and cost tuning belong outside this 03-feature-engineering brief.
## Evidence pack carried with 03-feature-engineering
- Raw subscriber records with plan tier, tenure months, support contacts, monthly spend snapshot pointer plus exact row counts.
- Dated run log linking each 03-feature-engineering build decision to its output table.
- Before/after comparison table kept beside the Churn feature slice tables.
- Rejected-rows file with rule codes for the 03-feature-engineering audit trail.
- One-page Feature Engineering (Tabular Codes) glossary defining every column the Churn feature slice emits.
## Reviewer walkthrough for Churn feature slice
- Reviewer opens 03-feature-engineering inputs and reproduces row counts unaided.
- Reviewer traces one rejected row from quarantine back to subscriber records with plan tier, tenure months, support contacts, monthly spend.
- Reviewer confirms no encoding statistics leak from holdout into train without extra explanation.
- Reviewer closes the Feature Engineering (Tabular Codes) session with two written follow-ups.
