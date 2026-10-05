# Lab 15 — Vision: On-Call Excellence for DR

## The Standard
Failover is a rehearsed muscle, not a document hunt. RTO/RPO numbers are on the dashboard with last-drill dates. Any on-call can cut over in 30 minutes with copy-paste commands — and knows when to hold instead.

## What Great Looks Like
- **Proven, not promised**: timed restore + timed cutover this quarter, published vs RTO/RPO.
- **Two regions, one pipeline**: identical IaC, secrets, migrations; drift diffed daily.
- **Gates over gut**: lag-within-RPO + secondary smoke green required before DNS flips.
- **Fenced by default**: old primary read-only on promotion; split-brain structurally impossible.
- **Honest RPO comms**: "writes after 14:02 may be lost (lag window)" — stated, not hidden.

## Anti-Patterns
- 200-page DR PDF nobody timed; backup green, restore corrupt.
- TTL 86400 on the failover record; cutover "done" but clients pinned for a day.
- Manual click-ops secondary missing three secrets; verification skipped "to save time."
- Two commanders promoting both sides; merge nightmare for weeks.

## Habits
1. Quarterly game-day owned, dated, timed; findings tracked to done.
2. Daily drift + lag + backup-age digest in standup channel.
3. Every migration idempotent; every conn string parameterized (CI checks).
4. Tabletop first, live drill second, real failover third.

## Interview Signal
Strong: RTO budget breakdown, lag-gate decision, fence + verify + failback detail. Weak: "we have backups in S3, we'll figure out restore if needed."
