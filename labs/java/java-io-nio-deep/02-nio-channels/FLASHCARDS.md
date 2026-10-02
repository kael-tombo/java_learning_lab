# FLASHCARDS — NIO Channels

| # | Front | Back |
|---|-------|------|
| 1 | Channel vs Buffer roles? | Channel = OS handle; Buffer = memory you manage (position/limit/flip). |
| 2 | `flip()` does what? | limit=position, position=0 — write-mode → read-mode. |
| 3 | Forgot `flip()` symptom? | Reads return nothing; no exception. |
| 4 | Scatter read in one call? | `channel.read(ByteBuffer[])` fills buffers in order. |
| 5 | Gather write? | `channel.write(ByteBuffer[])` drains buffers in order. |
| 6 | Missing TRUNCATE_EXISTING? | Stale tail bytes when new content is shorter. |
| 7 | mmap lifetime vs channel? | Independent — mapping outlives `close()`; unmap explicitly. |
| 8 | Windows mapped-file delete? | AccessDenied until unmapped (`Unsafe.invokeCleaner`). |
| 9 | READ_ONLY write attempt? | `ReadOnlyBufferException`. |
| 10 | `transferTo` return value? | Bytes moved — may be short; loop to completion. |
| 11 | Zero-copy meaning? | Kernel-to-kernel (sendfile), no user-space copy. |
| 12 | Whole-file `allocate(size)` risk? | O(S) heap — OOM on huge files; chunk or map instead. |
| 13 | Short file + scatter? | Trailing buffers partial — honor `remaining()`, not capacity. |
| 14 | `wrap` vs `allocate+put`? | `wrap` = zero-copy view; `allocate+put` = copy. |
| 15 | Scatter/gather syscall count? | One syscall for N buffers vs N syscalls. |
