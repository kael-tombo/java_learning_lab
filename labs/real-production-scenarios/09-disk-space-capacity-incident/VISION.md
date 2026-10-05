# VISION — Lab 09: On-Call Excellence for Capacity

## What Great Looks Like
- TTF dashboard per mount; page at <24h, never at 100%.
- Every writer capped (rotation/quota/sizeLimit); reclaim is one runbook page.
- Growing disk without fixing leak is called out, not celebrated.

## Habits
1. Check `df -h` + `df -i` together, every triage.
2. Truncate open logs; verify with lsof.
3. Weekly growth-trend review per service.
4. Drill disk-full in staging quarterly.
5. Separate partitions for logs/docker/data.

## Anti-Habits
- rm-ing WAL/snapshots by hand; grow-only fixes; debug-logging left on.

## Maturity Ladder
L0 % alerts → L1 TTF alerts → L2 caps everywhere → L3 auto-rotate/prune + lifecycle → L4 forecast + auto-expand with guardrails.

## Interview Signal
Quote TTF math + reclaim order + cap that prevents recurrence.
