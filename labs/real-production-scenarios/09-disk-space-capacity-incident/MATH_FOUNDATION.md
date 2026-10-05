# MATH FOUNDATION — Lab 09: Capacity / Growth Math

## 1. Time-to-Full
- TTF(hours) = availBytes / growthBytesPerHour.
- 50GB / 3GB/h ≈ 16.7h → page (threshold 24h). 200GB / 0.5GB/h = 400h → ticket.

## 2. Floor Sizing
- Floor = dailyGB × retentionDays × 1.3. Logs 20GB/d × 7d × 1.3 = 182GB.
- Snapshots 20GB/d × 14d × 1.3 = 364GB; cut to 7d → 182GB (saves 182GB).

## 3. Log Footprint Bound
- 100MB × 30 files = 3GB + current; totalSizeCap 5GB hard bound per service.
- 10 replicas × 5GB = 50GB fleet; fits 200GB log disk with 4x headroom.

## 4. Inode Math
- 1M session files × 4KB = 4GB bytes but 1M inodes; 2M-inode FS → 50% on tiny files.
- Fix: store sessions in Redis/DB, not files; or tmpfs with TTL.

## 5. Growth vs SLO Analogy
- Disk headroom like error budget: spend rate (GB/h) vs refill (reclaim/expand). Freeze writers when <24h TTF, like deploy freeze on low budget.

## 6. Worked Examples
1. Avail 15% of 500GB=75GB, growth 5GB/h → 15h → critical.
2. Image cache 80GB, prune until=72h frees 45GB → TTF 15h→24h.
3. WAL 2GB/h × 24h retention = 48GB reserved; doubling retention needs +48GB.

## 7. Takeaways
- Alert on TTF, not just %; every writer gets a cap + owner.
