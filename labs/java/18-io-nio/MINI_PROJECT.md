# MINI PROJECT — I/O & NIO: Static File Server

## Goal (2 weeks, ~8–10h)
Build a static-file server with safe uploads, range reads, checksums, and a blocking-vs-NIO comparison — no leaks, no path traversal, no OOM.

## Requirements
### Functional
1. Serve directory over sockets (or `HttpServer`): GET file, HEAD metadata, byte-range support (`Range: bytes=a-b`) via `FileChannel.transferTo` / mapped region.
2. Safe upload: write temp file + SHA-256, then `ATOMIC_MOVE`; reject `..` traversal via normalized-path containment check.
3. `Files.walkFileTree` indexer: size index + search by glob; symlink loop protection (`FOLLOW_LINKS` with cycle detect or skip).
4. `ByteBuffer` copy path with explicit `flip/clear`, direct-vs-heap flag, checksum match test.
5. Dual server mode: blocking + virtual threads vs single-thread Selector NIO; flag-switchable.
### Non-functional
- try-with-resources everywhere; max upload cap (e.g., 100MB) with 413; explicit UTF-8 for names/headers.
- 16+ tests: traversal blocked, atomic-replace crash-safe, range bytes exact, checksum equal, symlink no-hang, concurrent downloads.
- README: zero-copy diagram + blocking-vs-NIO verdict table (conns, p99, LOC).
- Load: 200 concurrent downloads of 50MB without heap > 1GB (streaming proof).

## Phases
### Week 1 — Safe Files (4–5h)
- Serve/head/range, upload-atomic, traversal tests.
- Deliverable: curl-verified file ops.
### Week 2 — NIO + Proof (4–5h)
- Selector mode, direct-buffer flag, load test + verdict.
- Deliverable: benchmark table + hardening report.

## Evaluation Rubric (100 pts)
| Criterion | Excellent (20) | Pass (12–14) | Fail (<10) |
|-----------|----------------|--------------|------------|
| Safety | Traversal+atomic+cap tested | Present | Missing |
| Buffer correctness | flip/compact explained + tested | Works | Corrupt output |
| Range/transfer | Exact bytes, zero-copy used | Works | Full-slurp |
| Dual mode | Both run, measured verdict | Both run | One mode |
| Tests + load | 16+ tests, 200-conn proof | 10+ tests | Happy-path only |

Pass ≥ 70. Stretch: `AsynchronousFileChannel` variant; ETag/If-None-Match caching.
