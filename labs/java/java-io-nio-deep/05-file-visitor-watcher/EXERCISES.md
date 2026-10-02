# EXERCISES — Visitor & Watcher

## 1. Extension trap (beginner)
Call `findByExtension(dir, "txt")` (no dot) on the fixture. Which extra
files match, if any? Fix the matcher to require the dot and add a test.

## 2. `visitFileFailed` strictness (beginner)
Make one fixture file unreadable (chmod/ACL), run `findByExtension`
(skips, `CONTINUE`) vs `deleteTree` (aborts). Argue which default is right
for each operation (query vs mutation).

## 3. Pre-order vs post-order delete (intermediate)
Move the `Files.delete(dir)` from `postVisitDirectory` to
`preVisitDirectory` and run. Record the exception. Explain why no
topological order other than post-order can delete a tree.

## 4. OVERFLOW storm (intermediate)
Write 5,000 files into a watched dir in a tight loop with a slow consumer
(`sleep 5ms` per event batch). Capture the `OVERFLOW` event. Implement
the rescan-on-overflow recovery (`findByExtension` reconciliation).

## 5. Recursive watcher (advanced)
`watchDirectory` is single-dir. Build a recursive watcher: register
existing subdirs, and on `ENTRY_CREATE` of a directory, register it too.
Handle the race (files created between listing and registration) with an
initial `listRecursive` reconciliation after each new registration.
