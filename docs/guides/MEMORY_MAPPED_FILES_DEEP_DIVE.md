# Memory-Mapped Files & Windows File Locking — Deep Dive

> Why did 3 tests in `07-file-io` pass their assertions yet fail the build
> with `AccessDeniedException: mapped.dat` during `@TempDir` cleanup?
> This guide traces the bug from OS kernel to one-line fix.

## 1. THEORY — Three ways to read a file

| Approach | How it works | Best for |
|----------|--------------|----------|
| `InputStream` read loop | Bytes copied kernel → user buffer per `read()` syscall | Small files, simplicity |
| `FileChannel` + `ByteBuffer` | Fewer syscalls, explicit buffers | Large sequential reads |
| `FileChannel.map()` (mmap) | OS maps file pages directly into process address space; **no copy**, page faults load data on demand | Large files, random access, multi-GB comparison |

Mental model: a mapped file is like the OS laying the file on your desk
instead of handing you pages one at a time. Fast — but the OS keeps a grip
on the file until you explicitly say "I'm done" (**unmap**).

### 1.1 The trap: `channel.close()` does NOT unmap

```java
MappedByteBuffer buffer = channel.map(READ_ONLY, 0, size);
channel.close();   // channel is closed…
buffer.get(0);     // …but the mapping is STILL ALIVE, file still locked
```

On Linux, deleting a mapped-but-closed file usually works (POSIX allows
unlinking open files). On **Windows, it does not** — the delete fails with
`AccessDeniedException`, and JUnit's `@TempDir` cleanup (which deletes the
whole temp directory after each test) blows up:

```
java.io.IOException: Failed to delete temp directory ...junit8833513979111673875
Suppressed: AccessDeniedException: ...\mapped.dat
```

Note the subtlety: **assertions passed** (`Tests run: 40, Failures: 0`).
Only the *cleanup* errored (`Errors: 3`). The bug is invisible on Linux CI
and explodes on Windows dev machines — a classic platform-dependent bug,
and therefore a great interview story.

### 1.2 Where our code mapped without unmapping (two sites)

**Site 1 — `MemoryMappedFile`** (`EliteFileIOTraining.java:554`):
```java
public void close() throws IOException {
    channel.close();   // BUG: buffer still mapped → file locked on Windows
}
```

**Site 2 — `compareFilesMemoryMapped`** (used for files ≥ 10 MB):
```java
ByteBuffer buffer1 = channel1.map(READ_ONLY, position, remaining);
ByteBuffer buffer2 = channel2.map(READ_ONLY, position, remaining);
if (!buffer1.equals(buffer2)) return false;  // BUG: early return leaks BOTH mappings
```
The 20 MB performance test (`testPerformance_LargeFileComparison`) always
took this path — hence the third failure on `large_perf1.txt`.

## 2. CODE_DEEP_DIVE — The fix

### 2.1 First attempt (failed — and why it is instructive)

```java
var cleanerMethod = mapped.getClass().getMethod("cleaner");
```
This worked on JDK 8–16 but fails on JDK 21+ due to strong encapsulation
(JPMS): internal `cleaner()` is no longer reflectively accessible. Our
`catch (Exception ignored)` silently swallowed it — mappings leaked, tests
still failed. Lesson: **a catch block that ignores everything can hide the
very signal you need**. We caught it only because the test still failed.

### 2.2 Correct fix — `Unsafe.invokeCleaner` (public API since Java 9)

```java
private static void unmap(ByteBuffer buffer) {
    if (buffer instanceof MappedByteBuffer mapped) {
        try {
            Class<?> unsafeClass = Class.forName("sun.misc.Unsafe");
            java.lang.reflect.Field theUnsafe =
                unsafeClass.getDeclaredField("theUnsafe");
            theUnsafe.setAccessible(true);
            Object unsafe = theUnsafe.get(null);
            unsafeClass.getMethod("invokeCleaner", ByteBuffer.class)
                       .invoke(unsafe, mapped);
        } catch (Exception ignored) {
            // Best-effort: GC will eventually release the mapping.
        }
    }
}
```
`sun.misc.Unsafe` sounds scary, but `invokeCleaner(ByteBuffer)` is the
*documented* way to unmap — no `--add-opens` flags required.

Applied in both sites:

```java
// Site 1: explicit resource release
public void close() throws IOException {
    unmap(buffer);      // release OS mapping FIRST
    channel.close();
}

// Site 2: unmap every chunk, even on early return
try {
    if (!buffer1.equals(buffer2)) return false;
} finally {
    unmap(buffer1);
    unmap(buffer2);
}
```

Result: `Tests run: 40, Failures: 0, Errors: 0` → **BUILD SUCCESS**.
The `finally` also fixes the early-return leak that code review should
have caught.

### 2.3 Design lesson — who owns the resource?

The deeper principle: **`map()` returns a resource; every resource needs
an owner and a release path**. Channels have try-with-resources; mappings
do not (no `AutoCloseable`). So we built the release into the two owners:
the `MemoryMappedFile` wrapper and the compare loop. Whenever you see an
API that acquires without an obvious release, that is where your bug —
and your interview answer — lives.

## 3. MATH_FOUNDATION — Why chunk at 1 MB?

```java
long chunkSize = 1024 * 1024;
for (long position = 0; position < size; position += chunkSize) { ... }
```
Mapping a whole 20 MB file is fine, but mapping a 20 GB file is not
(address-space pressure, page-table cost). Chunking bounds the mapped
window to 1 MB regardless of file size → **O(1) address-space cost**,
O(n) time. The 1 MB constant trades mapping syscalls (one per chunk)
against window size — the same shape of trade-off as the 8 KB copy buffer
in `copyFileWithProgress`.

## 4. EXERCISES

1. **Reproduce**: revert `unmap(buffer)` in `close()`, run
   `mvn -f 01-core-java/07-file-io/pom.xml verify` on Windows. Observe the
   3 `AccessDeniedException`s. Re-apply the fix.
2. **Early-return hunt**: find the `return false` inside the map loop.
   Explain why `finally` (not code after the `if`) is required.
3. **Portability essay** (5 lines): why does this bug hide on Linux?
   (Hint: POSIX unlink semantics vs Windows mandatory locking.)
4. **Silent-catch audit**: our first `catch (Exception ignored)` hid the
   JPMS failure. Add a `System.err.println` or logger to the catch, rerun
   with the old reflection code, and watch the signal reappear.

## 5. QUIZ

1. Does closing a `FileChannel` unmap its `MappedByteBuffer`s?
2. Why did assertions pass but the build still fail?
3. Why does this bug appear on Windows but often not on Linux?
4. What is wrong with `getMethod("cleaner")` on JDK 21+?
5. Why `try/finally` around `buffer1.equals(buffer2)`?

<details><summary>Answers</summary>

1. No. Mapping lifetime is independent of channel lifetime — you must unmap explicitly.
2. Failures are assertion violations; errors are infrastructure (here, `@TempDir` cleanup). Ours were cleanup errors.
3. Windows enforces mandatory file locks (delete of a mapped file fails); POSIX allows unlinking files with open handles/mappings.
4. Strong encapsulation (JPMS) — internal APIs are not reflectively accessible. Use `Unsafe.invokeCleaner`, the supported path.
5. The `return false` path would otherwise leak both chunk mappings every time files differ.

</details>

## 6. FLASHCARDS

- Q: mmap vs read loop? → A: mmap = OS maps pages into address space, no per-read copy; best for large/random access.
- Q: close(channel) unmaps? → A: No — separate lifetimes.
- Q: Windows vs Linux delete of mapped file? → A: Windows denies; Linux unlinks.
- Q: Supported unmap API since Java 9? → A: `sun.misc.Unsafe.invokeCleaner(buffer)`.
- Q: Failures vs Errors in Surefire? → A: failures = assertions; errors = unexpected exceptions (often cleanup).

## 7. MINI_PROJECT

Write a `LargeFileComparer` that compares two 50 MB files three ways
(byte loop, chunked mmap, checksum pre-check + mmap) and prints time +
result. Requirements: every mapping unmapped in `finally`; run on Windows
with `@TempDir`; all tests green including cleanup. Bonus: graph time vs
chunk size (256 KB / 1 MB / 4 MB).

## 8. REAL_WORLD_PROJECT

Production incident模拟: a log-ingestion service memory-maps rotated log
segments but leaks mappings on the "files differ, return early" path.
After 24 h on Windows, rotation fails with `AccessDeniedException` and
disk fills. Write the post-mortem: root cause, why Linux staging did not
catch it, the `finally`-based fix, and the regression test (`@TempDir` +
differing large files + assertion that the directory deletes cleanly).
