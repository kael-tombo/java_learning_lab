# CODE_DEEP_DIVE — Visitor & Watcher `MainImplementation`

Package `com.java.io.nio.lab05`.

## 1. `findByExtension` (lines 22–38)

- Anonymous `SimpleFileVisitor` overriding two methods: `visitFile` adds
  matches (`endsWith(extension)` — note: extension must include the dot,
  `".txt"`, or `"atxt"`-style names false-positive), `visitFileFailed`
  returns `CONTINUE` so one unreadable file never aborts the walk.
- `main` asserts exactly 2 `.txt` files in the fixture (`a.txt`, `sub/c.txt`).

## 2. `totalSize` (lines 43–53)

- `long[] size = {0}` — a one-element array as a mutable box, because
  anonymous-class captures must be final/effectively-final. (Modern
  alternative: `AtomicLong`.) Sums `attrs.size()` — no extra `Files.size`
  syscall per file.
- `main` asserts `size > 0` only — a smoke bound, not an exact figure
  (exact would couple the test to fixture byte counts).

## 3. `deleteTree` (lines 58–72)

- Files deleted in `visitFile`; directories in `postVisitDirectory` —
  **post-order is mandatory**: deleting a dir before its contents throws
  `DirectoryNotEmptyException`. `main` verifies `!Files.exists(deleteDir)`.
- No `visitFileFailed` override here (unlike `findByExtension`) — a locked
  file aborts the delete with an exception. Deliberate strictness worth
  knowing about.

## 4. `watchDirectory` (lines 78–95)

- try-with-resources on the `WatchService` itself; registers all three
  kinds; `poll(timeoutMs)` (not blocking `take()`) so tests stay bounded.
- `key == null` → `"timeout"`; empty poll → `"no-events"`; else first
  event as `KIND: filename` + `key.reset()` (re-arm — forgetting this is
  silent deregistration).
- `main` covers both paths: quiet dir → `"timeout"`; then an async
  `supplyAsync` watcher + 200 ms sleep + file creation → asserts
  `ENTRY_CREATE`/`ENTRY_MODIFY` prefix. The sleep-then-create ordering is
  what makes the timing deterministic.

## 5. `listRecursive` (lines 100–108)

- `Files.walk` in try-with-resources (open directory stream!), relativized
  against `startDir`, empty root filtered, sorted, collected. `main`
  asserts `a.txt`, `b.java`, `sub`, and `sub/c.txt` with both separators
  (`sub\\c.txt || sub/c.txt`) — the Windows/Unix portability guard.
