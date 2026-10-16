# Exploratory Analysis - Real-World Project: Retail basket exploration pack
## Problem
store transactions with basket size, tender type, hour band, promo flag. Success means a reviewer can rerun the 03-exploratory-analysis flow from raw files to final tables without asking for missing steps.
## Architecture (cross-tabs, group-wise summaries, QQ inspection, permutation spot-checks)
Core chain runs promo lift computed within hour bands first to avoid time-of-day confounding.
Method set in play: cross-tabs, group-wise summaries, QQ inspection, permutation spot-checks.
## Build sequence
1. Cross-tab promo flag against hour band with row and column shares.
2. Summarize basket size by tender type using median, IQR, and n.
3. Inspect QQ shape of log basket size before quoting any mean.
4. Permutation-shuffle the promo label 1000 times for one observed gap as reference.
5. Stratify the promo comparison within morning, midday, evening bands.
6. Close with ranked follow-up questions ordered by expected decision value.
## Acceptance checks
- cross-tabs show both shares plus raw counts for the 03-exploratory-analysis dossier.
- QQ reading recorded as approximately normal or not with reason checked against 03-exploratory-analysis logs.
- permutation reference reports its 1000-shuffle construction reproduced on rerun of 03-exploratory-analysis steps.
- stratified promo gaps reported per band not pooled only stored with the 03-exploratory-analysis artifact set.
- follow-ups ranked with one-line rationale each signed off inside the 03-exploratory-analysis review note.
## Limits of Retail basket exploration pack
Textbook methods only; streaming, serving, and cost tuning belong outside this 03-exploratory-analysis brief.
## Evidence pack carried with 03-exploratory-analysis
- Raw store transactions with basket size, tender type, hour band, promo flag snapshot pointer plus exact row counts.
- Dated run log linking each 03-exploratory-analysis build decision to its output table.
- Before/after comparison table kept beside the Retail basket exploration pack tables.
- Rejected-rows file with rule codes for the 03-exploratory-analysis audit trail.
- One-page Exploratory Analysis glossary defining every column the Retail basket exploration pack emits.
## Reviewer walkthrough for Retail basket exploration pack
- Reviewer opens 03-exploratory-analysis inputs and reproduces row counts unaided.
- Reviewer traces one rejected row from quarantine back to store transactions with basket size, tender type, hour band, promo flag.
- Reviewer confirms cross-tabs show both shares plus raw counts without extra explanation.
- Reviewer closes the Exploratory Analysis session with two written follow-ups.
