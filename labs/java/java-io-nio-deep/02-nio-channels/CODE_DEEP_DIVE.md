# CODE_DEEP_DIVE — NIO Channels `MainImplementation`

Package `com.java.io.nio.lab02`; file
`src/main/java/com/java/io/nio/lab02/MainImplementation.java`.

## 1. `readFile` / `writeFile` (lines 21–39)

- `readFile` allocates `ByteBuffer.allocate((int) channel.size())` — the
  whole file in one heap buffer. Simple, but O(file size) memory: fine for
  the lab's temp files, wrong for gigabytes (stream or map instead).
- `writeFile` wraps with `ByteBuffer.wrap(...)` (no copy) and opens with
  `CREATE + WRITE + TRUNCATE_EXISTING` — the standard create-or-overwrite
  triple. Missing `TRUNCATE_EXISTING` leaves stale tail bytes when the new
  content is shorter — a real production bug.
- `main` round-trips `"Hello NIO Channels!"` and asserts equality.

## 2. `scatterRead` / `gatherWrite` (lines 44–64)

- Buffers are allocated per `bufferSizes` and **each `flip()`ed after the
  single `channel.read(buffers)` call** — `flip` is per-buffer, and
  forgetting any one of them yields an empty view with no exception.
- `main` writes `"ABCDEFGHIJ"` and scatters into `(4,4,2)`, asserting
  `"ABCD"/"EFGH"/"IJ"` via `array()/remaining()`. Note: scattering stops
  at EOF — short files leave trailing buffers partially filled (position
  tells how much is valid).

## 3. `memoryMappedWrite` / `memoryMappedRead` (lines 69–83)

- Each call maps `[0, position+4)` fresh via `RandomAccessFile` + channel,
  writes/reads one int, then closes the channel **without unmapping**.
  On Windows, repeated calls in a loop accumulate mappings and lock the
  file — the exact failure mode fixed in `01-core-java/07-file-io` with
  `Unsafe.invokeCleaner` (see the memory-mapped deep-dive guide). The
  lab's `main` maps only 4 times so it passes, but callers should know.
- `READ_WRITE` vs `READ_ONLY` modes must match the access; writing through
  a `READ_ONLY` mapping throws `ReadOnlyBufferException`.

## 4. `transferTo` (lines 88–94)

- Single call moves the full range; returns bytes transferred (assert the
  return value in production — partial transfers are legal).
- `main` writes `"Zero-copy test"`, transfers, and asserts the destination
  content matches exactly.
