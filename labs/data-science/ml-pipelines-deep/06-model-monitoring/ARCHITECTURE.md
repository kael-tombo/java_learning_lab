# Model Monitoring - Architecture

## Components
- Event logger: captures predictions, versions, features, and timestamps.
- Aggregator: builds hourly and daily rollups of score mix and null rates.
- Comparator: contrasts current windows with the reference window (PSI/KS-style checks).
- Alert engine: evaluates high-precision paging rules and links runbooks.
- Dashboard: shows trends, slice breakdowns, and label-maturity markers.

## Data flow
- Serving path emits events asynchronously so monitoring never blocks predictions.
- Aggregates feed both dashboards and the alert engine on separate cadences.
- Ground truth joins by key when it arrives; quality metrics recompute on mature windows.

## Storage
- Raw events retent short-term; rollups keep long-term for trend analysis.
- Reference windows are pinned snapshots, updated deliberately with review.
- Incident history links alerts to runbooks and follow-up test cases.

## Boundaries
- Monitoring reads production traffic but never mutates serving state.
- Alert actions are limited to paging and dashboard annotation; mitigation is a separate, reviewed step.

## Reference management
- Reference windows are immutable snapshots with a recorded reason and owner.
- Refreshes create a new pinned snapshot; the old one stays for back-comparison.
- Schema or pipeline changes force a reference review before monitors resume.

## Slice pipeline
- Every event carries slice keys (region, device, cohort) populated at serving time.
- Rollups group by slice key so per-segment metrics cost one pass, not N queries.
- New slices register explicitly; unregistered dimensions stay out of paging rules.

## Runbook binding
- Each paging rule stores its runbook pointer beside the threshold definition.
- Pages render slice, signal, maturity age, and first triage steps together.
- Runbook edits follow the same review as rule edits; stale steps page too.

## Retention tiers
- Raw events live days, hourly rollups months, daily rollups years.
- Trend analysis reads rollups; forensics reads raw events inside retention.
- Deletion jobs run on schedule; monitors confirm volume drops are expected.

## Failure isolation
- A broken comparator must not silence paging: rules evaluate on last-good rollups.
- Dashboard outages never gate alerts; the two paths share nothing but input.
- Backfill replays rewrite rollups idempotently keyed by window and version.
