# Time Series (Decomposition) - Real-World Project: Energy demand decomposition study
## Problem
hourly meter demand spanning two full seasonal cycles with holiday dips. Success means a reviewer can rerun the 04-time-series flow from raw files to final tables without asking for missing steps.
## Architecture (classical decomposition, ACF/PACF inspection, ADF and KPSS checks, seasonal-naive baseline)
Core chain runs trend, seasonal, residual separated additively after variance stabilization note.
Method set in play: classical decomposition, ACF/PACF inspection, ADF and KPSS checks, seasonal-naive baseline.
## Build sequence
1. Plot raw demand and annotate holidays plus meter-gap intervals.
2. Decompose into trend, daily/weekly seasonal, residual components.
3. Read ACF/PACF spikes at daily and weekly lags with numbers.
4. Run ADF and KPSS and report both statistics with 0.05 thresholds.
5. Fit seasonal-naive baseline carrying forward same-hour-last-week values.
6. Attribute residual spikes to dated events or mark them unexplained.
## Acceptance checks
- both ADF and KPSS statistics reported with 0.05 reading for the 04-time-series dossier.
- ACF/PACF lag numbers quoted for daily and weekly spikes checked against 04-time-series logs.
- seasonal-naive baseline error stated as reference MAE reproduced on rerun of 04-time-series steps.
- residual spike table maps dates to causes or unknown stored with the 04-time-series artifact set.
- gap intervals listed rather than interpolated silently signed off inside the 04-time-series review note.
## Limits of Energy demand decomposition study
Textbook methods only; streaming, serving, and cost tuning belong outside this 04-time-series brief.
## Evidence pack carried with 04-time-series
- Raw hourly meter demand spanning two full seasonal cycles with holiday dips snapshot pointer plus exact row counts.
- Dated run log linking each 04-time-series build decision to its output table.
- Before/after comparison table kept beside the Energy demand decomposition study tables.
- Rejected-rows file with rule codes for the 04-time-series audit trail.
- One-page Time Series (Decomposition) glossary defining every column the Energy demand decomposition study emits.
## Reviewer walkthrough for Energy demand decomposition study
- Reviewer opens 04-time-series inputs and reproduces row counts unaided.
- Reviewer traces one rejected row from quarantine back to hourly meter demand spanning two full seasonal cycles with holiday dips.
- Reviewer confirms both ADF and KPSS statistics reported with 0.05 reading without extra explanation.
- Reviewer closes the Time Series (Decomposition) session with two written follow-ups.
