# FLASHCARDS — Visitor & Watcher

| # | Front | Back |
|---|-------|------|
| 1 | walkFileTree vs Files.walk? | Tree: mutations w/ lifecycle hooks, O(depth). Stream: queries, O(n), needs try-with-resources. |
| 2 | Delete order? | Post-order (files then dir) — pre-order throws DirectoryNotEmpty. |
| 3 | `visitFileFailed → CONTINUE`? | Skip-and-continue policy for queries; strict abort for mutations. |
| 4 | `long[1]` capture trick? | Final-box workaround for anonymous classes; prefer AtomicLong today. |
| 5 | `attrs.size()` vs `Files.size`? | Reuse visit attributes — avoids doubling stat syscalls. |
| 6 | Extension match needs? | Include the dot (".txt") or extension-less names false-positive. |
| 7 | WatchService vs polling cost? | ~0 idle + O(events) vs O(n/p) stats forever. |
| 8 | OVERFLOW means? | Bounded queue overrun — rescan/reconcile, don't trust log. |
| 9 | Missing `key.reset()`? | Silent deregistration — events stop, no error. |
| 10 | `poll` vs `take`? | Bounded (tests) vs blocking forever (daemons). |
| 11 | Registration scope? | One dir only — subdirs need own registrations. |
| 12 | Quiet-dir test expects? | `"timeout"` — deterministic negative control. |
| 13 | Files.walk leak? | Open dir stream — try-with-resources mandatory. |
| 14 | Separator-agnostic assert? | Accept both `sub\c.txt` and `sub/c.txt`. |
| 15 | Create-then-watch race? | Reconcile with a listing after each new registration. |
