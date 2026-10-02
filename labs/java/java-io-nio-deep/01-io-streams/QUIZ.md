# QUIZ — I/O Streams

## 1. Why is single-byte `FileInputStream.read()` slow on large files?
<details><summary>Answer</summary>One syscall per byte (~1M syscalls/MB). Buffering amortizes to ~S/B syscalls.</details>

## 2. In `bufferedCopy`, why `write(buf, 0, n)` instead of `write(buf)`?
<details><summary>Answer</summary>`read(buf)` may return fewer bytes than the buffer length (short read, always the tail chunk). Writing the full buffer would append stale bytes.</details>

## 3. What happens if you forget to close a `BufferedOutputStream`?
<details><summary>Answer</summary>The buffered tail is never flushed — the destination file is silently truncated. try-with-resources prevents this.</details>

## 4. `writeInt(42); writeDouble(3.14)` must be read back in what order, and why?
<details><summary>Answer</summary>Same order, same types (`readInt` then `readDouble`). The format is positional with no schema — the reader cannot detect field boundaries otherwise.</details>

## 5. How does `writeUTF` differ from `getBytes(UTF_8)`?
<details><summary>Answer</summary>`writeUTF` uses modified UTF-8 with a 2-byte length prefix (≤65,535 bytes); it must be read with `readUTF`, never with raw byte reads.</details>

## 6. In `findPattern`, why push back `b` *before* the lookahead bytes?
<details><summary>Answer</summary>Pushback is LIFO: pushing `b` first then lookahead replays the original byte order on subsequent reads.</details>

## 7. What does `findPattern` return when the pattern starts at offset 0?
<details><summary>Answer</summary>`-1`, because `prev` is initialized to -1 and no byte precedes the match.</details>

## 8. Why is the pushback buffer sized exactly `pattern.length`?
<details><summary>Answer</summary>Worst case needs to un-read 1 (`b`) + (`m-1`) lookahead bytes = `m` bytes. A smaller buffer throws on `unread`.</details>

## 9. Why does `concatenate` use `Vector` + `elements()` instead of `ArrayList`?
<details><summary>Answer</summary>`SequenceInputStream` requires an `Enumeration<InputStream>` — a pre-generics API. `Vector.elements()` provides one; `ArrayList` has no equivalent.</details>

## 10. `read(buf)` returns 0 — possible? What must callers do?
<details><summary>Answer</summary>Yes for non-blocking/custom streams (not typical for files). Correct loop condition is `!= -1` (as in the lab), never `> 0`, so zero-length reads don't terminate the copy early.</details>
