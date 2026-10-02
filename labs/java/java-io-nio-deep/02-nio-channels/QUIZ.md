# QUIZ — NIO Channels

## 1. After `channel.read(buf)`, what must you call before reading from `buf`, and why?
<details><summary>Answer</summary>`flip()` — switches limit=position, position=0. Without it the buffer still looks empty/full-write-mode and reads return nothing.</details>

## 2. `writeFile` opens with CREATE + WRITE + TRUNCATE_EXISTING. What breaks without TRUNCATE_EXISTING?
<details><summary>Answer</summary>Shorter new content leaves the old tail: writing 5 bytes over 20 leaves 15 stale bytes. File length only grows, never shrinks.</details>

## 3. Scatter read: one syscall fills 3 buffers. What determines the split?
<details><summary>Answer</summary>Buffer capacities in order — bytes fill buffer[0], then [1], then [2]. Sizes must be chosen from the message layout (e.g. 12-byte header).</details>

## 4. `MappedByteBuffer` survives `channel.close()`. Consequence on Windows?
<details><summary>Answer</summary>File stays locked (AccessDeniedException on delete) until explicitly unmapped via `Unsafe.invokeCleaner`. Linux usually allows the unlink.</details>

## 5. Writing through a READ_ONLY mapping throws what?
<details><summary>Answer</summary>`ReadOnlyBufferException`.</details>

## 6. What does `transferTo` return, and why must callers check it?
<details><summary>Answer</summary>Bytes actually transferred — may be short (interrupt, limits). Robust callers loop until the full range moves.</details>

## 7. Why is `transferTo` called zero-copy?
<details><summary>Answer</summary>Bytes move kernel-to-kernel (sendfile); no user-space buffer copy and fewer context switches per chunk.</details>

## 8. `readFile` allocates `channel.size()` bytes. What's wrong with this for huge files?
<details><summary>Answer</summary>O(file size) heap — a multi-GB file exhausts memory. Stream in chunks or map a window instead.</details>

## 9. `scatterRead` on a short file: what do trailing buffers contain?
<details><summary>Answer</summary>Partially filled — `position` shows valid bytes; the rest is unwritten zeros. Always consume via `remaining()`, not capacity.</details>

## 10. `ByteBuffer.wrap(bytes)` vs `allocate` + `put`: what differs?
<details><summary>Answer</summary>`wrap` views the array with zero copy (writes visible in the array); `allocate+put` copies. `wrap` needs no `flip` before writing-out, but does before reading back.</details>
