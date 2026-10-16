# Experimentation - Real-World Project: Checkout A/B plan and analysis
## Problem
checkout funnel with visitor, cart-start, purchase events plus device stratum. Success means a reviewer can rerun the 07-experimentation flow from raw files to final tables without asking for missing steps.
## Architecture (randomization design, power calculation, t and chi-square tests, peeking guards)
Core chain runs primary metric fixed upfront as purchase per visitor; device used only as stratum.
Method set in play: randomization design, power calculation, t and chi-square tests, peeking guards.
## Build sequence
1. Fix primary metric, unit of randomization, and minimum detectable effect in writing.
2. Compute required sample size at alpha 0.05 and power 0.80 for that effect.
3. Randomize by visitor hash with stratification on device class.
4. Monitor sample-ratio mismatch daily without testing the primary metric early.
5. Analyze with two-sample t for rates and chi-square for device-balance check.
6. Report effect with 95% interval plus a ship, iterate, or stop recommendation.
## Acceptance checks
- alpha 0.05 and power 0.80 stated with the MDE value for the 07-experimentation dossier.
- sample-size formula inputs preserved in the plan checked against 07-experimentation logs.
- SRM check procedure documented with threshold reproduced on rerun of 07-experimentation steps.
- 95% interval shown beside the p-value stored with the 07-experimentation artifact set.
- recommendation maps explicitly to the interval not hype signed off inside the 07-experimentation review note.
## Limits of Checkout A/B plan and analysis
Textbook methods only; streaming, serving, and cost tuning belong outside this 07-experimentation brief.
## Evidence pack carried with 07-experimentation
- Raw checkout funnel with visitor, cart-start, purchase events plus device stratum snapshot pointer plus exact row counts.
- Dated run log linking each 07-experimentation build decision to its output table.
- Before/after comparison table kept beside the Checkout A/B plan and analysis tables.
- Rejected-rows file with rule codes for the 07-experimentation audit trail.
- One-page Experimentation glossary defining every column the Checkout A/B plan and analysis emits.
## Reviewer walkthrough for Checkout A/B plan and analysis
- Reviewer opens 07-experimentation inputs and reproduces row counts unaided.
- Reviewer traces one rejected row from quarantine back to checkout funnel with visitor, cart-start, purchase events plus device stratum.
- Reviewer confirms alpha 0.05 and power 0.80 stated with the MDE value without extra explanation.
- Reviewer closes the Experimentation session with two written follow-ups.
