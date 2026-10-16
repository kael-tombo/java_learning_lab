# Model Monitoring - History

## Shared background
- Martin Kleppmann, Designing Data-Intensive Applications (O'Reilly, 2017), systematized batch versus stream processing and log-based data integration used across these labs.
- Sculley, Holt, Golovin and colleagues, "Hidden Technical Debt in Machine Learning Systems" (NIPS 2015), documented how serving, glue code, pipelines, and monitoring dominate production ML cost.
- Breck and colleagues' ML Test Score rubric extended that line of work into scored production-readiness checks for data, models, and infrastructure.

## Monitoring specifics
- Binned divergence checks in the PSI family come from credit-risk scorecard monitoring, where population stability is tracked per score band.
- The Kolmogorov-Smirnov comparison of empirical CDFs is a classical nonparametric statistics tool repurposed here for drift checks.
- Paging discipline with runbook links comes from site-reliability engineering, where alert precision decides whether pages are trusted.
- Slice-aware evaluation follows from fairness and subgroup analysis literature: aggregates hide segment failures.
- Label-delay handling mirrors forecasting and risk practice, where outcomes mature after decisions and provisional reporting is standard.
- Scorecard-PSI deepened: per-band stability tracking turns raw score
  movement into an attributable shift — bin 3's share moving from 0.08
  toward 0.12 dominates the sum, which is why the exercise moves that
  exact bin. The mechanism is relative-size accounting, not a verdict.
- KS deepened: the maximum CDF gap needs no binning choice, so it
  complements PSI where bin edges are contested; the snippet gap of
  0.250 at x = 0.52 names both size and location, and location directs
  the slice investigation that follows.
- SRE-paging deepened: precision-over-pages is the trust metric — the
  snippet's 0.300 precision with 0.750 recall describes a monitor that
  catches most incidents while paging often, the classic case for
  demoting to dashboard and keeping only sharp rules paging.
- Slice-evaluation deepened: subgroup analysis moved from fairness
  literature into operations because averages hide segment failures;
  per-slice positive rates are the instrument, and the argmax segment
  in the exercise is the triage answer in miniature.
- Maturity-reporting deepened: forecasting and risk desks long marked
  fresh estimates provisional until outcomes landed; the six-day
  maturity filter here is that habit applied to labels, keeping official
  metrics on joined ground truth and orientation charts provisional.
- Telemetry-presence deepened: silent monitors fail by stopping, not by
  spiking, so volume and last-received timestamps are first-class
  signals; alerting on absence is the habit that keeps flat lines
  honest.
