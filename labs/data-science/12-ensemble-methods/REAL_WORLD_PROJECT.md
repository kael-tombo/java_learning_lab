# Ensemble Methods - Real-World Project: Tabular default-risk ensemble comparison
## Scenario
borrower records with income, utilization, delinquency counts, loan purpose. Success means a reviewer can rerun the 12-ensemble-methods flow from raw files to final tables without asking for missing steps.
## Design (bagging and random forests, gradient boosting, stacking, OOB and CV scoring)
Core chain runs all comparisons under 5-fold CV with ROC-AUC plus PR-AUC on imbalanced labels.
Method set in play: bagging and random forests, gradient boosting, stacking, OOB and CV scoring.
## Execution steps
1. Baseline a single depth-limited tree with 5-fold ROC-AUC recorded.
2. Bag a random forest and report OOB error beside CV scores.
3. Boost with shrinkage comparing two learning rates at fixed depth.
4. Stack tree, forest, boosting outputs under logistic meta-learner.
5. Compare ROC-AUC and PR-AUC side by side with fold deviations.
6. Attribute gains via permutation importance on the winning ensemble.
## Pass criteria
- 5-fold ROC-AUC present for every candidate for the 12-ensemble-methods dossier.
- PR-AUC shown given class imbalance checked against 12-ensemble-methods logs.
- OOB error reported for the forest arm reproduced on rerun of 12-ensemble-methods steps.
- boosting rate comparison table retained stored with the 12-ensemble-methods artifact set.
- permutation importance lists top five features signed off inside the 12-ensemble-methods review note.
## Limits of Tabular default-risk ensemble comparison
Textbook methods only; streaming, serving, and cost tuning belong outside this 12-ensemble-methods brief.
## Evidence pack carried with 12-ensemble-methods
- Raw borrower records with income, utilization, delinquency counts, loan purpose snapshot pointer plus exact row counts.
- Dated run log linking each 12-ensemble-methods build decision to its output table.
- Before/after comparison table kept beside the Tabular default-risk ensemble comparison tables.
- Rejected-rows file with rule codes for the 12-ensemble-methods audit trail.
- One-page Ensemble Methods glossary defining every column the Tabular default-risk ensemble comparison emits.
## Reviewer walkthrough for Tabular default-risk ensemble comparison
- Reviewer opens 12-ensemble-methods inputs and reproduces row counts unaided.
- Reviewer traces one rejected row from quarantine back to borrower records with income, utilization, delinquency counts, loan purpose.
- Reviewer confirms 5-fold ROC-AUC present for every candidate without extra explanation.
- Reviewer closes the Ensemble Methods session with two written follow-ups.
