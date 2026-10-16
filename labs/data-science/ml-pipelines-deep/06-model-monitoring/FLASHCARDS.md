# Model Monitoring - Flashcards

Q: Data drift vs concept drift? A: Inputs move vs the mapping moves.
Q: What is label delay? A: Ground truth arrives after prediction.
Q: PSI formula? A: Sum of (a-e)*ln(a/e) over bins.
Q: KS statistic? A: Maximum gap between the two empirical CDFs.
Q: Alert precision? A: Fraction of pages worth acting on.
Q: Alert recall? A: Fraction of real incidents that paged.
Q: F1 formula? A: 2PR/(P+R) at one operating point.
Q: Why mark fresh windows provisional? A: Labels have not matured yet.
Q: Official metrics use which windows? A: Mature ones with joined ground truth.
Q: What is a feedback loop? A: Model outputs shape future training data.
Q: First check on a drift page? A: Pipeline health, then slices, then model.
Q: Why pin reference windows? A: So comparisons stay anchored and deliberate.
Q: Silent-monitor failure mode? A: Telemetry stops; flat lines look fine.
Q: Missing-data guard? A: Alert on absent volume, not only bad values.
Q: Every alert needs what? A: A runbook link.
Q: PSI input form? A: Binned shares, reference vs current.
Q: PSI zero means? A: Identical binned distributions.
Q: Empty-bin hazard? A: ln(0) undefined; smooth or merge.
Q: KS needs binning? A: No; uses the pooled sorted grid.
Q: KS blind spot? A: Direction and importance of the gap.
Q: Snippet PSI value? A: 0.0378, led by bins 0 and 3.
Q: Snippet KS value? A: 0.250 at x = 0.52.
Q: Snippet alert profile? A: Precision 0.300, recall 0.750: noisy, sensitive.
Q: Fixed vs sliding windows? A: Independent comparisons vs faster, correlated.
Q: Short vs long windows? A: Noisy vs slow; pair fast dashboards with gated alerts.
Q: Equal-maturity rule? A: Compare windows only at the same label age.
Q: Provisional marking? A: Fresh windows labeled incomplete, never official.
Q: Retraining label rule? A: Mature windows only.
Q: Trial monitor lifecycle? A: Expire by date unless precision earns paging.
Q: Seasonality guard? A: Same-season reference or deseasonalize first.
Q: Volume-drop check? A: Event counts and last-received timestamps.
Q: Pipeline-first triage? A: Deploys and schema changes before model causes.
Q: Incident-to-case loop? A: Confirmed incidents join the pinned evaluation set.
Q: Postmortem records? A: Cause, detection lag, monitor changes.
Q: Cardinality cap why? A: Unbounded slices explode comparator cost.
Q: Monitor-the-monitor metrics? A: Alert volume, precision, time-to-detect.
