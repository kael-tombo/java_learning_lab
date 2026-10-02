# CODE_DEEP_DIVE — I/O Streams `MainImplementation`

All references are to
`src/main/java/com/java/io/nio/lab01/MainImplementation.java`.

## 1. `bufferedCopy(File, File)` (lines 18–30)

```java
byte[] buf = new byte[8192];
while ((n = bis.read(buf)) != -1) { bos.write(buf, 0, n); total += n; }
```

- Reads **chunks**, not bytes: `read(buf)` returns the count actually read,
  which may be less than 8192 (especially the last chunk). Hence
  `write(buf, 0, n)` — writing the full buffer would corrupt the tail.
- Returns total bytes: the `main` self-check asserts 12 for `"Hello World!"`.
- Both streams close automatically, output flushed on close. Forgetting to
  close a `BufferedOutputStream` **loses the buffered tail** — the most
  common real-world bug in this pattern.

## 2. `writePrimitives` / `readPrimitives` (lines 35–49)

- `DataOutputStream` over a `ByteArrayOutputStream` lets the lab test the
  binary format without touching disk.
- `writeUTF` uses **modified UTF-8 with a 2-byte length prefix** (max
  65,535 bytes) — not the same as `String.getBytes(UTF_8)`. You must read
  with `readUTF`; mixing with raw reads corrupts the stream.
- `readPrimitives` returns `List.of(int, double, String)` — autoboxed, and
  `List.of` is immutable (callers cannot append).

## 3. `findPattern(byte[], byte[])` (lines 55–73) — the subtle one

Single-byte lookahead parser with pushback:

1. Read byte `b`; remember `prev` (the byte *before* any match) — the
   return value is `prev`, not the match position.
2. If `b` equals `pattern[0]`, read the remaining `pattern.length - 1`
   bytes and compare via `matches(lookahead, pattern, 1)`.
3. On mismatch, **push everything back**: `pbs.unread(b)` then
   `pbs.unread(lookahead, 0, read)`. Pushback order is LIFO — `b` goes back
   first, then the lookahead bytes, so the next `read()` replays the
   original sequence.
4. `prev = b` updates only on the non-matching path, which is why the
   self-check `findPattern({1,2,3,4,5,6}, {4,5}) == 3` holds.

Edge cases to notice: `read` may return fewer bytes than requested
(`read > 0` guard); pattern at offset 0 returns `prev == -1`; the pushback
buffer is sized exactly `pattern.length`, so a longer lookahead would throw.

## 4. `concatenate(byte[]...)` (lines 85–99)

- `Vector<InputStream>` + `streams.elements()` is required because
  `SequenceInputStream` takes an `Enumeration` (a pre-generics API).
  The 256-byte read buffer is deliberately small to exercise multi-chunk
  reads across part boundaries.
- `main` asserts `"AB"+"CD"+"EF" == "ABCDEF"` — concatenation is byte-exact,
  no separators added.
