# Time Series (Forecasting) - Real-World Project: Bike-share demand forecast harness
## Brief
daily station rentals with weather covariates and event-day outliers. Success means a reviewer can rerun the 05-time-series flow from raw files to final tables without asking for missing steps.
## Components (ARIMA/ETS selection, rolling-origin validation, prediction intervals, residual diagnostics)
Core chain runs origins roll forward monthly; intervals scored by empirical coverage at 80 and 95%.
Method set in play: ARIMA/ETS selection, rolling-origin validation, prediction intervals, residual diagnostics.
## Work plan
1. Hold out the final 60 days as untouched evaluation span.
2. Select ARIMA/ETS orders on the training span using AIC comparison.
3. Roll origins forward in 30-day steps refitting each window.
4. Score MAE and RMSE per origin plus interval coverage at 80 and 95%.
5. Diagnose residuals with Ljung-Box reading and outlier date list.
6. Publish the forecast table with intervals and a failure-modes note.
## Done when
- 60-day holdout never used in order selection for the 05-time-series dossier.
- AIC comparison table retained for candidate orders checked against 05-time-series logs.
- coverage reported at both 80 and 95% nominal levels reproduced on rerun of 05-time-series steps.
- Ljung-Box result quoted with degrees of freedom stored with the 05-time-series artifact set.
- failure-modes note names event-day behavior signed off inside the 05-time-series review note.
## Limits of Bike-share demand forecast harness
Textbook methods only; streaming, serving, and cost tuning belong outside this 05-time-series brief.
## Evidence pack carried with 05-time-series
- Raw daily station rentals with weather covariates and event-day outliers snapshot pointer plus exact row counts.
- Dated run log linking each 05-time-series build decision to its output table.
- Before/after comparison table kept beside the Bike-share demand forecast harness tables.
- Rejected-rows file with rule codes for the 05-time-series audit trail.
- One-page Time Series (Forecasting) glossary defining every column the Bike-share demand forecast harness emits.
## Reviewer walkthrough for Bike-share demand forecast harness
- Reviewer opens 05-time-series inputs and reproduces row counts unaided.
- Reviewer traces one rejected row from quarantine back to daily station rentals with weather covariates and event-day outliers.
- Reviewer confirms 60-day holdout never used in order selection without extra explanation.
- Reviewer closes the Time Series (Forecasting) session with two written follow-ups.
