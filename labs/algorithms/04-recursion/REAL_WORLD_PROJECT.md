# REAL_WORLD_PROJECT — Recursion in Production: Filesystem Scanner
> Production use-case: permission-aware directory walk + size rollup (depth-bounded).

## 1. Scenario
- Backup agent walks customer volumes (symlinks, deep nesting, permission gaps).
- Constraint: no crash on 50k-deep node_modules chains; symlink cycles must not loop.
- Choice: recursive clarity for ≤256 depth, auto-fallback to explicit stack beyond.
- Output: per-dir sizes + cycle/skip report.

## 2. Architecture
```
walk(root) → recurse w/ depth budget → on budget-exceed switch to ArrayDeque stack
```
- Visited-device+inode set (cycle guard); depth counter + `MAX_DEPTH=512` flag.
- Sentinel-safe memo for repeated subtree stats (content-hash cache).
- Audit: skipped (perm/cycle/depth) counts per run.

## 3. War-Story
- Incident: recursive walk on symlink loop (`a→b→a`) + 40k-deep chain → StackOverflow + infinite revisit.
- Symptom: agent crash-loop on one tenant; rest fine (data-dependent).
- Root cause: missing base guards (no visited set, no depth budget, sentinel collision hid cached errors).
- Fix: inode set + depth budget + iterative fallback + `StackOverflowError`→controlled abort with resume cursor.
- Lesson: recursion ships with a depth + cycle budget, not just bases.

## 4. Metrics (1M-file volume)
| Metric | Before | After | Delta |
|--------|--------|-------|-------|
| Crash rate | 1/200 volumes | 0/5000 | −100% |
| p99 walk | crash | 8.2s | fixed |
| Cycle rewalks | ∞ (loop) | 0 | fixed |
| Skipped-audit coverage | 0% | 100% | +100pp |
| Max depth handled | ~9k | 200k+ | 22× |

## 5. Prevention Checklist
- [ ] Depth budget + fallback (tested to 10⁵).
- [ ] Cycle set (dev+inode) + symlink policy.
- [ ] Base/negative/perm fixtures.
- [ ] Sentinel-collision review (boolean[] where needed).
- [ ] Resume cursor on abort.
- [ ] Overflow-safe size sums (long).
- [ ] Crash→abort-with-report (never silent).
- [ ] Depth histogram metric per fleet.

## 6. What "Good" Looks Like
- Zero crash-loops; every skip explained; deep volumes complete.

## 7. Stretch
- Parallel subtree walks (ForkJoin) with work-stealing note.

## 8. Sourced field notes (fetched Oct 2026 — verify before citing)
- Java stack/StackOverflowError behavior: https://docs.oracle.com/javase/8/docs/api/java/util/Collections.html
- Recursion mechanics + depth limits: https://en.wikipedia.org/wiki/Recursion_(computer_science)
