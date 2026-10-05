# VISION — On-Call Excellence for Memory Leaks

## 1. The Future State
No memory incident surprises on-call. Heap trends page hours before OOM, dumps capture automatically, and any engineer can confirm a leak from a dashboard in 2 minutes without waking a JVM expert.

## 2. What "Good" Looks Like
- Every service ships with `-XX:+HeapDumpOnOutOfMemoryError`, GC logs, and heap-after-Full-GC dashboards by default.
- Alerts fire on trend slope, not just threshold — paging with estimated T_oom ("12h to OOM").
- Runbooks link directly to `jcmd` one-liners and MAT screenshots, not tribal knowledge.

## 3. Behaviors to Build
Calm evidence-first triage: capture histo/dump before restart, restart to protect users, then diagnose from artifacts. Blameless postmortems that ask "why did retention ship?" not "who shipped it?".

## 4. Anti-Vision
3 a.m. restart loops with no dumps, heap size bumped blindly each incident, caches growing unbounded because "we'll add eviction later".

## 5. Your Commitment
This week: enable auto-dump + heap-trend alert on one service. Next: add a soak test asserting Old Gen returns to baseline. Excellence is trend visibility plus bounded memory by construction.

> On-call excellence = see the leak coming, protect users fast, prove the cause from data.
