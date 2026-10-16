# Model Monitoring - Security

## Data protection
- Monitoring stores predictions and features; apply the same redaction as serving logs.
- Restrict slice dimensions that could re-identify individuals.
- Encrypt event streams and rollup stores at rest and in transit.

## Alert integrity
- Only reviewed changes may edit alert rules; log every edit with author.
- Separate alert-definition permission from acknowledge permission.
- Treat silence as a signal: monitor for missing telemetry, not just bad values.

## Adversarial awareness
- Attackers may probe monitors; sudden volume or pattern shifts deserve review.
- Feedback-fed labels can be poisoned; validate label sources before retraining.
- Pin reference windows so an attacker cannot move the baseline quietly.

## Access
- Dashboards default to least privilege; export of raw events needs approval.

## Pipeline tampering
- Validate schema at ingest; reject or quarantine partitions that violate ranges.
- Sign reference snapshots so quiet baseline moves are detectable.
- Log every rule and reference edit with author and reviewed reason.

## Label integrity
- Treat label joins as privileged writes; unreviewed sources stay provisional.
- Quarantine model-influenced labels from retraining inputs by default.
- Recompute official metrics from signed label tables, not ad-hoc extracts.

## Monitor spoofing
- Attackers may flood events to move current windows; cap per-source volume.
- Authenticate telemetry emitters; unsigned events never enter rollups.
- Cross-check volume against serving counters to catch injected traffic.

## Retention and privacy
- Slice dimensions multiply re-identification risk; approve high-cardinality slices.
- Redact raw identifiers in stored events; join by token where policy requires.
- Time-box raw retention; rollups carry trends forward without the detail.

## Runbook safety
- Runbooks execute under least privilege; destructive steps need second approval.
- Test mitigation commands on staging after every runbook edit.
- Version runbooks beside the rules they serve so pages and steps never desync.
