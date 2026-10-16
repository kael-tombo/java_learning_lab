# MLOps Orchestration - Visual Guide

## DAG
```text
        [ingest]
            |
       [validate]--(fail--> stop, keep prod)
            |
        [train]
         /     \
 [evaluate]   [package]
         \     /
       [gate]--(fail--> notify, no promote)
            |
       [promote]
```

## Backoff
```text
attempt:  0    1    2    3    4    5
wait:     1s   2s   4s   8s   16s  30s(cap)
```

## Lineage pointer
```text
run-042 = data(v14) + code(abc1234) + params(lr=0.01,seed=7) + env(pinned)
```

## Triggers
```text
cron:   ----*----*----*----      (cadence)
event:  -------X--------X---      (data lands, alert fires)
```

## Queues
```text
scheduled:  [run][run][run]      (cadence lane, never starved)
event:      [run]                (arrival lane)
backfill:   [replay]===(capped)==> versioned paths
```

## Promotion record
```text
promote-117 = who(owner) + when(ts) + lineage(run-042) + gates(all green)
```
