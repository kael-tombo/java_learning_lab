# THEORY — Lab 09: Disk-Space / Capacity Incident

## 1. Mechanics: How Disks Fill
- Unrotated logs (GB/hour at debug), unbounded uploads/tmp, runaway snapshots, Docker overlay growth, DB WAL retention.
- Fill → writes fail (No space left) → pods Evicted / CrashLoop → DB read-only → cascade.
- Inode exhaustion distinct from bytes: millions of small files, same symptoms.

## 2. Detection Signals
- `node_filesystem_avail_bytes` / `df -h` <15% warn, <5% critical; inode % similarly.
- Log growth rate (bytes/min), tmp dir size, image/pull cache, PV usage.
- Alerts: predict-full-hours = avail / growthRate <24h pages.
- K8s events: `Evicted: The node had condition: [DiskPressure]`.

## 3. Triage Hierarchy
1. Stop bleeding: raise log level, pause heavy jobs, throttle uploads.
2. Reclaim fast: rotate/truncate logs, clear tmp, prune Docker/images, expire snapshots.
3. Expand: grow PV/resize disk, add nodes, move cold data.
4. Fix root: rotation policy, quotas, retention, lifecycle rules.

## 4. Log Rotation Essentials
- logback/log4j size+time rolling, maxHistory, totalSizeCap; stdout + sidecar vs file.
- Never `>> app.log` forever; compress + ship to central store, keep local 1–7d.

## 5. K8s Capacity Controls
- ephemeral-storage requests/limits evict hogs early; `emptyDir` sizeLimit.
- Image GC thresholds; separate partitions for /var/log, /var/lib/docker, data.
- Node-pressure eviction order; PodDisruptionBudgets during reclaim.

## 6. DB / Snapshot Growth
- WAL/binlog retention + backup window; snapshot schedule vs disk headroom.
- Growth math: GB/day × retention = floor requirement + 30% headroom.

## 7. Forecasting Math
- FullIn(hours) = availBytes / growthBytesPerHour. Alert when <24–48h.
- Burn analogy: disk budget like error budget; freeze writes-generating jobs when red.

## 8. Common Mistakes
- `rm` open file (space not freed until handle closed; use truncate).
- Deleting active WAL/snapshot breaks recovery — expire via tool, not rm.
- Growing disk without fixing leak — buys hours, repeats SEV.

## 9. Triage Order
`df -h` → `du -sh` top dirs → `lsof +L1` deleted-open → rotate/prune → grow → policy fix.

## 10. Takeaways
- Monitor growth rate, not just usage %; cap every writer with rotation/quota.
