# Feature Stores — Visual Guide

## As-of join (read bottom to top by ts)
Feature history for u1:

  ts=30  value=3.0   <-- future relative to label t=25: EXCLUDE
  ------- label (u1, t=25) -------
  ts=20  value=2.0   <-- greatest ts <= t: USE THIS
  ts=10  value=1.0   <-- older: ignore

Result: training row (u1, t=25, value=2.0).

## Offline vs online
```
raw events --> [transform v1] --> OFFLINE LOG (all ts)
                                      |           |
                                 as-of join    materializer
                                      |           |
                               training rows   ONLINE KV (latest)
```

## Skew picture
```
training path:  raw --[0.5x+1]--> 1.5 2.0 2.5 3.0
serving stale:  raw --[0.5x+0]--> 0.5 1.0 1.5 2.0
gap per element:                   1.0 each -> maxdiff 1.0
```

## TTL picture (label t=100, TTL=30)
```
ts=10 age=90 DROP
ts=50 age=50 DROP
ts=90 age=10 KEEP
ts=95 age=5  KEEP
kept=2 dropped=2 coverage=0.5
```

## Versioning picture
```
v1 rows: kept for model A (pinned)
v2 rows: backfilled, validated, live for model B
registry: model -> version set (rollback = repoint)
```
