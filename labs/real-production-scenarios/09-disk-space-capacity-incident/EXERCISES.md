# EXERCISES — Lab 09: Disk / Capacity

## Exercise 1: Find the Hog (15 min)
Given `df -h` 98% + `du` output, name top dir + growth culprit (logs vs tmp vs images). Write reclaim order.

## Exercise 2: Safe Reclaim (20 min)
Practice: truncate open log (`: > app.log` / `truncate -s 0`) vs `rm` (explain handle leak). Verify with `lsof +L1` + `df`.

## Exercise 3: Rotation Policy (20 min)
Write logback rolling (100MB, 30 files, 5GB cap, gzip) + retention doc. Compute worst-case footprint.

## Exercise 4: Docker Prune Drill (15 min)
`docker system df` → `prune -a --filter until=72h` → verify freed + no running image removed.

## Exercise 5: Inode Hunt (15 min)
`df -i` 99% with bytes free → find small-file dir (`find | wc -l`), safe cleanup + code fix (session files).

## Exercise 6: Forecast Alert (15 min)
Avail 50GB, growth 3GB/h → full in ~16h. Write Prometheus predict-full alert + severity.

## Exercise 7: ephemeral-storage Guard (15 min)
Add requests/limits + emptyDir sizeLimit to hogging pod; show eviction targets hog not neighbor.

## Exercise 8: Snapshot Retention (15 min)
Compute: 20GB/day × 14d = 280GB + 30% = 364GB floor. Trim to 7d + offsite; show savings.

## Exercise 9: Tabletop: DB Read-Only (20 min)
Disk full → DB read-only. Steps: stop writers, reclaim logs, grow PV, verify writes, re-enable jobs.

## Exercise 10: Post-Mortem (15 min)
5-Whys to missing rotation + no growth alert. 3 actions with owners.
