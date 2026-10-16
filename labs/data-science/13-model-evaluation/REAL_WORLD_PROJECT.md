# Model Evaluation - Real-World Project: Evaluation harness plus model card
## Problem
scored loan outcomes with predicted probabilities and segment tags. Success means a reviewer can rerun the 13-model-evaluation flow from raw files to final tables without asking for missing steps.
## Architecture (confusion analysis, ROC/PR curves, calibration bins, K-fold with held-out lock)
Core chain runs threshold chosen on validation; held-out scored once and reported as-is.
Method set in play: confusion analysis, ROC/PR curves, calibration bins, K-fold with held-out lock.
## Build sequence
1. Lock a held-out split before any threshold discussion begins.
2. Cross-validate with k=5 reporting ROC-AUC plus PR-AUC deviations.
3. Plot ROC and PR curves with prevalence noted beside PR.
4. Bin predictions into deciles and tabulate observed versus expected rates.
5. Pick the operating threshold on validation using stated cost trade-off.
6. Publish a one-page model card with limits and segment caveats.
## Acceptance checks
- k=5 folds with deviation bars on both AUCs for the 13-model-evaluation dossier.
- prevalence printed alongside PR curve checked against 13-model-evaluation logs.
- decile calibration table complete with counts reproduced on rerun of 13-model-evaluation steps.
- threshold rationale cites costs not vibes stored with the 13-model-evaluation artifact set.
- model card lists two known failure segments signed off inside the 13-model-evaluation review note.
## Limits of Evaluation harness plus model card
Textbook methods only; streaming, serving, and cost tuning belong outside this 13-model-evaluation brief.
## Evidence pack carried with 13-model-evaluation
- Raw scored loan outcomes with predicted probabilities and segment tags snapshot pointer plus exact row counts.
- Dated run log linking each 13-model-evaluation build decision to its output table.
- Before/after comparison table kept beside the Evaluation harness plus model card tables.
- Rejected-rows file with rule codes for the 13-model-evaluation audit trail.
- One-page Model Evaluation glossary defining every column the Evaluation harness plus model card emits.
## Reviewer walkthrough for Evaluation harness plus model card
- Reviewer opens 13-model-evaluation inputs and reproduces row counts unaided.
- Reviewer traces one rejected row from quarantine back to scored loan outcomes with predicted probabilities and segment tags.
- Reviewer confirms k=5 folds with deviation bars on both AUCs without extra explanation.
- Reviewer closes the Model Evaluation session with two written follow-ups.
