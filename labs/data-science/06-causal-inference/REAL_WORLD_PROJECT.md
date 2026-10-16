# Causal Inference - Real-World Project: Promo uplift observational study
## Scenario
mailed promo versus control customers with age band, prior spend, region. Success means a reviewer can rerun the 06-causal-inference flow from raw files to final tables without asking for missing steps.
## Design (DAG drafting, propensity matching, difference-in-differences, refutation checks)
Core chain runs DAG drawn before estimation; matched pairs checked for balance before outcome look.
Method set in play: DAG drafting, propensity matching, difference-in-differences, refutation checks.
## Execution steps
1. Draw the DAG naming confounders, mediators, colliders explicitly.
2. Estimate propensity scores and match treated units within caliper.
3. Report standardized mean differences before and after matching per covariate.
4. Compute the matched spend-lift estimate with 95% interval.
5. Run difference-in-differences on pre/post spend as second design.
6. Placebo-test by shuffling treatment labels and rerunning the estimator.
## Pass criteria
- DAG figure lists which variables are adjusted versus excluded for the 06-causal-inference dossier.
- post-match standardized differences below 0.1 for key covariates checked against 06-causal-inference logs.
- 95% interval accompanies the lift point estimate reproduced on rerun of 06-causal-inference steps.
- DiD parallel-trends plot shown for pre-periods stored with the 06-causal-inference artifact set.
- placebo permutation result reported alongside main estimate signed off inside the 06-causal-inference review note.
## Limits of Promo uplift observational study
Textbook methods only; streaming, serving, and cost tuning belong outside this 06-causal-inference brief.
## Evidence pack carried with 06-causal-inference
- Raw mailed promo versus control customers with age band, prior spend, region snapshot pointer plus exact row counts.
- Dated run log linking each 06-causal-inference build decision to its output table.
- Before/after comparison table kept beside the Promo uplift observational study tables.
- Rejected-rows file with rule codes for the 06-causal-inference audit trail.
- One-page Causal Inference glossary defining every column the Promo uplift observational study emits.
## Reviewer walkthrough for Promo uplift observational study
- Reviewer opens 06-causal-inference inputs and reproduces row counts unaided.
- Reviewer traces one rejected row from quarantine back to mailed promo versus control customers with age band, prior spend, region.
- Reviewer confirms DAG figure lists which variables are adjusted versus excluded without extra explanation.
- Reviewer closes the Causal Inference session with two written follow-ups.
