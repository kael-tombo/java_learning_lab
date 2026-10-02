# THEORY — File Visitor & WatchService (lab05)

## 1. Two traversal APIs, one choice

`MainImplementation` (lab05) shows both directory-walking styles:

- **`Files.walkFileTree` + `SimpleFileVisitor`**: event-driven, O(depth)
  stack, early termination via `SKIP_SUBTREE`/`TERMINATE`, per-file error
  policy via `visitFileFailed` (return `CONTINUE` to skip what you can't
  read — the lab does exactly this). Choose for: deletes, copies, size
  walks, anything needing lifecycle hooks (`preVisitDirectory`,
  `postVisitDirectory` — deletion *requires* post-order: files first,
  then the dir).
- **`Files.walk` (Stream)**: functional listing (`map`/`filter`/`sorted`/
  `collect` as in `listRecursive`). Must be in try-with-resources (it
  holds an open directory stream). Choose for: queries, listings,
  find-style filters.

## 2. WatchService: events, not polling

`watchDirectory` registers a dir for `ENTRY_CREATE/MODIFY/DELETE`, then
`watcher.poll(timeout)` returns a `WatchKey` whose `pollEvents()` batch
is drained, `key.reset()` re-armed. No polling loop burning CPU; the OS
pushes change notifications. The return encoding
(`KIND + ": " + filename`, `"timeout"`, `"no-events"`) keeps tests
deterministic: `main` first asserts a quiet dir yields `"timeout"`, then a
created file yields `ENTRY_CREATE`.

## 3. The three classic pitfalls (all visible in this lab)

1. **Overflow**: event queues are bounded — burst writes coalesce into
   `OVERFLOW` (the lab's single-event read would miss it; production code
   must handle/rescan). 2. **Registration is per-directory, not recursive**
   — new subdirs need their own registration. 3. **Key reset**: forgetting
   `key.reset()` silently unregisters the dir — events stop with no error.
