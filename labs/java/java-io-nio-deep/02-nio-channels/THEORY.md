# THEORY — NIO Channels (lab02)

## 1. From streams to channels + buffers

`java.io` streams move bytes implicitly. NIO (`java.nio.channels`) splits
the job in two: a **Channel** (the OS handle) and a **Buffer** (the memory
you control). You explicitly `read(buf)` into a buffer, `flip()` it from
write-mode to read-mode, consume, then `clear()`/`compact()` for reuse.
Every method in `MainImplementation` (lab02) follows this dance — miss the
`flip()` and you read zero bytes with no error, the classic NIO beginner
bug.

## 2. Scatter/gather: one syscall, many buffers

`scatterRead` issues a single `channel.read(ByteBuffer[])` that fills
multiple buffers in order (header/body/suffix split). `gatherWrite` does
the reverse. Fewer syscalls + zero reassembly copies — the same
amortization idea as lab01 buffering, applied to structured messages.

## 3. Memory-mapped files

`memoryMappedWrite/Read` map file pages into the process address space via
`channel.map(...)`. Reads/writes become memory accesses — no syscalls per
operation. **Warning carried over from `07-file-io`**: a mapping stays
alive after `channel.close()`; on Windows the file remains locked until
explicitly unmapped (`Unsafe.invokeCleaner`). See
`docs/guides/MEMORY_MAPPED_FILES_DEEP_DIVE.md`. Note lab02's implementation
maps fresh per call and never unmaps — fine for a demo, a leak in a loop.

## 4. Zero-copy transfer

`transferTo` (`src.transferTo(0, size, dst)`) asks the OS to move bytes
kernel-to-kernel (e.g. `sendfile`), bypassing user-space buffers entirely.
For file-to-file or file-to-socket copies this is the fastest option —
but it only works when both ends are channels the OS understands.
