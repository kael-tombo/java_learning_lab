# QUIZ — Visitor & Watcher

## 1. `walkFileTree` vs `Files.walk`: when each?
<details><summary>Answer</summary>walkFileTree: mutations/lifecycle (delete, copy — needs pre/post hooks, O(depth) memory). Files.walk stream: queries/listings (functional, but O(n) collected and needs try-with-resources).</details>

## 2. Why must directory deletion happen in `postVisitDirectory`?
<details><summary>Answer</summary>A directory must be empty before deletion — post-order deletes contents first. Pre-order throws `DirectoryNotEmptyException`.</details>

## 3. `visitFileFailed` returns `CONTINUE` in `findByExtension` but is absent in `deleteTree`. Effect?
<details><summary>Answer</summary>Find skips unreadable files (query robustness); delete aborts on locked files (strictness — partial deletes are worse than loud failure).</details>

## 4. `long[] size = {0}` — why an array?
<details><summary>Answer</summary>Anonymous-class captures must be final/effectively-final — the array is a mutable box. (Modern code: `AtomicLong`.)</details>

## 5. `key.reset()` forgotten — symptom?
<details><summary>Answer</summary>Silent deregistration: no error, events simply stop arriving for that dir.</details>

## 6. `poll(timeout)` vs `take()`?
<details><summary>Answer</summary>`poll` bounds waits (tests stay deterministic); `take` blocks forever — fine for daemons, fatal for tests.</details>

## 7. Burst of 5,000 creates, slow consumer. What arrives?
<details><summary>Answer</summary>Coalesced `OVERFLOW` — the queue is bounded and lossy. Correct response: rescan/reconcile, don't trust the event log.</details>

## 8. WatchService registration scope?
<details><summary>Answer</summary>Single directory only — subdirs (existing or created later) need their own registrations.</details>

## 9. Why both `sub\\c.txt` and `sub/c.txt` in the assert?
<details><summary>Answer</summary>Path separators differ Windows vs Unix — the test accepts either rendering of the same relative path.</details>

## 10. `Files.walk` resource hazard?
<details><summary>Answer</summary>It holds an open directory stream — must be in try-with-resources, or descriptors leak on every listing.</details>
