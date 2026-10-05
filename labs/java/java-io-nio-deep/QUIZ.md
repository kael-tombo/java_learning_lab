# Quiz — Java IO / NIO Deep (20 Q)

1. Blocking vs non-blocking channel difference?
> Non-blocking returns immediately; blocking parks thread until ready.
2. What are position, limit, capacity?
> Cursor, bound, max size of a Buffer.
3. flip() does what?
> limit=position, position=0 — prepares for read.
4. clear() vs compact()?
> clear resets; compact preserves unread bytes.
5. Heap vs direct ByteBuffer?
> Heap on GC heap; direct off-heap, faster IO, costlier alloc.
6. What is a Selector?
> Multiplexes ready channels onto one thread.
7. OP_ACCEPT vs OP_READ vs OP_WRITE?
> Ready-to-accept/connect/read/write events.
8. transferTo benefit?
> Zero-copy kernel path, fewer user/kernel crossings.
9. MappedByteBuffer risk?
> Holds file mapping; unmap only via Cleaner; may OOM virtual space.
10. FileChannel thread-safety?
> Safe for concurrent position-independent ops; position-based needs care.
11. WatchService OVERFLOW means?
> Events lost; rescan directory.
12. AsyncChannelGroup purpose?
> Thread pool backing async channels.
13. Why `Too many open files`?
> FD leak — unclosed channels/sockets.
14. CharsetEncoder vs String.getBytes?
> Encoder reports malformed input; getBytes replaces silently.
15. Scatter/gather use case?
> One syscall for header+body vectors.
16. Files.walk followlinks danger?
> Cycles — use NOFOLLOW or cycle detection.
17. Direct memory flag?
> `-XX:MaxDirectMemorySize`.
18. Selector wakeup() use?
> Unblock select() from another thread.
19. When to prefer classic IO?
> Simple scripts, small files, blocking semantics fine.
20. How to detect FD leak?
> `lsof -p <pid>`, `/proc/<pid>/fd`, metrics on open channels.
