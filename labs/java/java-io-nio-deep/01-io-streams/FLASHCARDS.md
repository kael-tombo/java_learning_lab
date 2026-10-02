# FLASHCARDS — I/O Streams

| # | Front | Back |
|---|-------|------|
| 1 | Byte vs character streams? | Bytes: binary, no encoding. Characters: text via Charset — always specify UTF_8. |
| 2 | Decorator pattern in `java.io`? | Nesting constructors composes behavior: `BufferedInputStream(FileInputStream(...))`. |
| 3 | Cost of unbuffered byte reads? | ~1 syscall/byte; buffer B bytes → ~S/B syscalls. |
| 4 | `read(buf)` return contract? | Bytes actually read, possibly < buf.length; -1 at EOF. Always use `write(buf,0,n)`. |
| 5 | try-with-resources close order? | Reverse of opening; output streams flush on close. |
| 6 | Data-stream ordering rule? | Write and read same order/types — format is positional, schema-less. |
| 7 | `writeUTF` format? | Modified UTF-8 + 2-byte length prefix; read only with `readUTF`. |
| 8 | Pushback buffer sizing? | ≥ max bytes ever un-read at once (= pattern length here). |
| 9 | Pushback replay order? | LIFO — push back in reverse of desired re-read order. |
| 10 | `findPattern` return value? | Byte *before* the match; -1 if pattern at offset 0 or absent. |
| 11 | `findPattern` worst case? | O(n·m): full m-compare at every position (all-`pattern[0]` text). |
| 12 | KMP improvement? | Failure function avoids re-scan: O(n+m). |
| 13 | `SequenceInputStream` input type? | `Enumeration<InputStream>` → hence `Vector.elements()`. |
| 14 | Forgetting to close buffered output? | Buffered tail lost — truncated file, no error. |
| 15 | Short reads — when? | Always possible (tail chunk, pipes, sockets); loop on `!= -1`. |
