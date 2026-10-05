# VISION — I/O & NIO

## Vision Statement
**Bytes move; avoid copying them** — correct I/O is resource discipline (close, flush, bound) plus choosing blocking vs non-blocking for the workload.

---
## Mental Models
### 1. Stream vs Channel vs Path
`InputStream/OutputStream` = byte flow; `Reader/Writer` = chars + charset; `Channel/Buffer` = blocks + memory control; `Path/Files` = modern file ops. Pick the layer, don't mix.
### 2. Buffer Discipline
`ByteBuffer`: fill → `flip()` → drain → `clear()/compact()`. Forgetting `flip` is the #1 NIO bug. Direct buffers dodge heap copy but cost allocate/free.
### 3. Blocking Scales People, Non-Blocking Scales Connections
One thread per socket is simple; Selector/async scales 10k idle connections. Complexity only pays past hundreds of concurrent sockets.
### 4. Files: Atomic + Bounded
Temp-then-`ATOMIC_MOVE`, try-with-resources everywhere, never `readAllBytes` on unbounded input, always explicit `Charset`.

---
## Decision Framework
| Question | Rule |
|----------|------|
| Simple file copy? | `Files.copy` / transferTo, not hand loops |
| Large file? | Stream (`Files.lines`) or memory-map chunks, never slurp |
| Many idle sockets? | NIO Selector / async; else blocking + virtual threads |
| Encoding? | Always `StandardCharsets.UTF_8`, never default |

---
## Career Trajectory
- **L1:** `Path/Files`, try-with-resources, copy/read/write, explicit charset.
- **L2:** `ByteBuffer` flip/clear, `FileChannel.transferTo`, `Files.walk` safely.
- **L3:** Selector non-blocking server, `AsynchronousFileChannel`, zero-copy tuning.
- **L4:** File-format/storage design, backpressure, mmap vs streaming tradeoffs.

---
## 4-Week Path
```
W1: Path/Files CRUD, walk/find, charset-safe read/write.
W2: ByteBuffer + FileChannel copy with checksums.
W3: Blocking socket server → virtual-thread version.
W4: Static-file server kata: atomic writes + mmap range + benchmark.
```
## Success Metrics
- [ ] Zero resource leaks under static analysis
- [ ] Explain flip/clear/compact from memory
- [ ] Justify blocking vs NIO per connection count
