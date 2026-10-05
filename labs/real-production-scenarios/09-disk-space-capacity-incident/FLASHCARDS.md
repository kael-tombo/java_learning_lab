# FLASHCARDS — Lab 09: Disk / Capacity

| Front | Back |
|---|---|
| `df -h` | Byte usage per mount |
| `df -i` | Inode usage per mount |
| `du -sh /*` | Top-dir size hunt |
| `du -sh * \| sort -rh \| head` | Ranked hog finder |
| `lsof +L1` | Deleted-but-open files holding space |
| Truncate vs rm | `: > file` frees now; rm waits for close |
| DiskPressure | K8s node condition triggering evictions |
| Evicted pod | Removed due to node pressure; check events |
| ephemeral-storage req/limit | Caps pod temp disk; evicts hogs |
| emptyDir sizeLimit | Bounds scratch volume |
| Image GC | Kubelet reclaims unused images at thresholds |
| `docker system df` | Image/container/volume disk breakdown |
| `docker system prune` | Reclaims unused Docker data |
| Log rolling | Size+time rotation with history cap |
| totalSizeCap | Worst-case log footprint bound |
| maxHistory | Days/files retained |
| Debug logging cost | GB/hour writer that fills disks fast |
| /var/log partition | Isolates log flood from data |
| /var/lib/docker partition | Isolates image growth |
| Tmp cleanup | cron + TTL on uploads/scratch |
| Quota | Per-tenant write cap |
| Retention policy | e.g., logs 7d local, snapshots 7d + offsite |
| Lifecycle rule | Auto-tier/delete cold objects |
| WAL / binlog | DB durability logs; retain per backup window |
| Never rm active WAL | Breaks PITR; expire via DB tool |
| Snapshot math | GB/day × days × 1.3 headroom |
| Predict-full alert | avail/growthRate <24h |
| Growth rate metric | bytes/min per dir (node exporter) |
| Node exporter | Filesystem + pressure metrics source |
| PV resize | Expand claim/disk after reclaim |
| Read-only DB | Write-protect mode when disk critical |
| Stop-the-bleed | Raise log level, pause jobs, throttle uploads |
| Reclaim order | Logs→tmp→images→snapshots→grow |
| Offsite backup | S3/GCS tier for snapshots, not local only |
| Compression | gzip logs/snapshots to cut footprint |
| Session-file leak | Small-file inode hog classic |
| find-count hunt | `find dir \| wc -l` for inode hog |
| Headroom 30% | Buffer above computed floor |
| Freeze writers | Halt log-heavy jobs when red |
| Post-mortem trio | Rotation + quota + growth alert |
| Interview line | "50GB/3GBh=16h; truncated, rotated, capped" |
| `truncate -s 0` | Zero file without killing handle |
| `journalctl --vacuum-size` | Cap systemd journal footprint |
| Log ship | Forward to central store, keep local short |
| Central retention | 30–90d searchable vs 7d local |
| Capacity review | Weekly growth trend per service |
| Burn analogy | Disk headroom like error budget |
| SEV rule | Writes failing = SEV1/2 by blast radius |
| Verify writes | Test insert/upload after recovery |
| Re-enable order | Jobs back gradually with monitoring |
| Document floor | GB/day math in runbook |
| Drill | Fill staging disk, practice reclaim |
| Anti-pattern grow-only | Buys hours, repeats outage |
| Separate data disk | DB on own PV, not root |
| Monitor inodes too | Alert both bytes and inodes |
| Top writer dashboard | Per-pod ephemeral usage ranking |
| Cleanup cron | Scheduled tmp/image/snapshot expiry |
| Owner per writer | Every GB/h source has rotation owner |
