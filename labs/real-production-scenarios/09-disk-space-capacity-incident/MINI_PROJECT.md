# MINI PROJECT — Lab 09: Fill, Find, Fix a Disk

## Objective
Fill a staging volume, triage fast, fix with rotation + caps.

## Part A — Reproduce (25 min)
1. Filler script writes 100MB/min logs + 1M small files to a test mount.
2. Observe `df` + `df -i` diverge; app writes fail; node reports DiskPressure (or simulate).

## Part B — Detect (15 min)
1. Run 60-second diagnose (`df`, `du`, `lsof`); name hog + TTF math.
2. Distinguish bytes-full vs inode-full from your numbers.

## Part C — Fix (40 min)
1. Reclaim: truncate logs, delete tmp>2d, prune images; record GB + inodes freed.
2. Add logback rotation (100MB/30/5GB) + ephemeral-storage limits.
3. Add TTF alert; verify write-test passes; document floor math.

## Deliverables
- Timeline + before/after `df` outputs + TTF calc.
- Config diffs + forecast alert rule.

## Stretch
- Journal vacuum + lifecycle rule for cold snapshots.

## Grading
Diagnosis (30%), safe reclaim (30%), caps+alert (25%), math (15%).
