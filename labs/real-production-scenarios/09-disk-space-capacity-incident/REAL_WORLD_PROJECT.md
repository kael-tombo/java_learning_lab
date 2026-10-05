# REAL WORLD PROJECT — Lab 09: Capacity War-Room

## 1. War-Room Timeline
| T | Event | Owner |
|---|---|---|
| T+0 | Writes fail: `No space left`, DB read-only | Monitor |
| T+3 | IC SEV2; `df` 100%, `du` pins /var/log (debug left on) | SRE |
| T+10 | Log level raised, jobs paused; truncate frees 60GB | Ops |
| T+20 | Prune images + tmp; snapshot expiry via tool | Platform |
| T+35 | PV expanded; writes verified | DBA/Ops |
| T+50 | Rotation + caps deployed; TTF green | IC closes |

## 2. Triage Runbook
1. `df -h` + `df -i`. 2. `du` top dirs. 3. `lsof +L1`. 4. Stop bleed → reclaim → grow → cap.

## 3. Commands
```bash
df -h; df -i
du -sh /var/log /tmp /var/lib/docker /data | sort -rh
: > /var/log/app/app.log; journalctl --vacuum-size=1G
docker system prune -a --filter "until=72h"
```

## 4. Metrics of Recovery
- Avail >20% + TTF >72h; writes succeed 10 min; zero Evicted; DB read-write.

## 5. Comms Template
> SEV2 disk-full, writes paused. Reclaim done, growing volume. ETA 20 min. Next :15.

## 6. Prevention
- Rotation everywhere, ephemeral caps, TTF alerts, weekly growth review, separate partitions, lifecycle rules.

## 7. Cost Template
Downtime × revenue + overtime + expanded storage + churn-risk; show floor math that would have prevented.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- Kubernetes node-pressure eviction: https://kubernetes.io/docs/concepts/scheduling-eviction/node-pressure-eviction/
- Kubernetes ephemeral storage management: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
- Redis persistence sizing (appendonly/RDB trade-offs): https://redis.io/docs/latest/operate/oss_and_stack/management/persistence/
