# Exploratory Data Analysis - Real-World Project: Rental listings EDA dossier
## Brief
rental adverts with price, floor area, bedroom count, posting lag, missing area entries. Success means a reviewer can rerun the 02-eda flow from raw files to final tables without asking for missing steps.
## Components (univariate distributions, grouped summaries, correlation scan, missingness audit)
Core chain runs price-per-area derived only where area present; never imputed silently; missingness cross-tabbed by poster type.
Method set in play: univariate distributions, grouped summaries, correlation scan, missingness audit.
## Work plan
1. Tabulate missingness per column and cross-tab missing area against poster type.
2. Plot price and area distributions with median, IQR, 1st/99th percentiles annotated.
3. Compare median price per bedroom band and per district with counts alongside.
4. Compute pairwise correlations among numeric columns and flag pairs above 0.8.
5. Isolate top 1% prices and verify whether area, bedrooms, or entry error explains them.
6. Record three falsifiable observations plus one disproof attempt for each.
## Done when
- every chart states sample size n after exclusions for the 02-eda dossier.
- medians reported with IQR rather than mean-only summaries checked against 02-eda logs.
- correlation table uses pairwise-complete rows with n shown reproduced on rerun of 02-eda steps.
- top-1% review classifies each case as explained or data error stored with the 02-eda artifact set.
- observations list includes at least one failed disproof note signed off inside the 02-eda review note.
## Limits of Rental listings EDA dossier
Textbook methods only; streaming, serving, and cost tuning belong outside this 02-eda brief.
## Evidence pack carried with 02-eda
- Raw rental adverts with price, floor area, bedroom count, posting lag, missing area entries snapshot pointer plus exact row counts.
- Dated run log linking each 02-eda build decision to its output table.
- Before/after comparison table kept beside the Rental listings EDA dossier tables.
- Rejected-rows file with rule codes for the 02-eda audit trail.
- One-page Exploratory Data Analysis glossary defining every column the Rental listings EDA dossier emits.
## Reviewer walkthrough for Rental listings EDA dossier
- Reviewer opens 02-eda inputs and reproduces row counts unaided.
- Reviewer traces one rejected row from quarantine back to rental adverts with price, floor area, bedroom count, posting lag, missing area entries.
- Reviewer confirms every chart states sample size n after exclusions without extra explanation.
- Reviewer closes the Exploratory Data Analysis session with two written follow-ups.
