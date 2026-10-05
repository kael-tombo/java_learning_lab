# QUIZ — Lab 09: Disk / Capacity (15 questions)

1. First check on "No space left"? — A) CPU B) `df -h` + `df -i` C) RAM D) DNS — **B**
2. Inode exhaustion means? — A) Bytes full B) File-count full, bytes may be free C) CPU D) Net — **B**
3. `rm` open log frees? — A) Instantly B) No, until handle closed; truncate instead C) Doubles D) Compresses — **B**
4. DiskPressure causes? — A) Faster B) K8s evictions C) Cheaper D) Nothing — **B**
5. Predict-full = ? — A) avail/growthRate B) CPU/RAM C) Random D) Uptime — **A**
6. Safe fast reclaim? — A) Delete WAL by hand B) Rotate/truncate logs, clear tmp, prune images C) rm root D) Reboot only — **B**
7. Log rotation caps? — A) Nothing B) Size×files + totalSizeCap C) CPU D) Net — **B**
8. ephemeral-storage limits? — A) Decor B) Evict hogs early C) Slower D) Bigger bills — **B**
9. Snapshot growth fix? — A) Keep forever B) Retention + offsite lifecycle C) Ignore D) rm active — **B**
10. Never delete? — A) Old tmp B) Active WAL/snapshot by hand C) Cache D) Old images — **B**
11. Growth 3GB/h, avail 50GB → full? — A) 150h B) ~16h C) 1h D) Never — **B**
12. 20GB/d×14d+30% ≈? — A) 20GB B) 364GB C) 20TB D) 0 — **B**
13. Separate partitions help? — A) No B) Log flood can't take down data disk C) Slower D) Costlier — **B**
14. Image GC does? — A)Deletes code B) Reclaims unused layers/images C) Grows disk D) Restarts — **B**
15. After growing disk must? — A) Nothing B) Fix leak + add growth alert C) Delete backups D) Disable metrics — **B**
