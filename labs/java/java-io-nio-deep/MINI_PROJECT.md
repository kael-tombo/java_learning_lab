# Mini Project — Fast File Indexer

## Goal
Index all `.java`/`.log` under a root: path, size, mtime, first-line preview. Sub-second on 10k files.

## Architecture
```
Files.walk(root) → filter → (bounded queue) → workers → index.dat
```
Workers: fixed pool (cores). Queue: ArrayBlockingQueue(256).

## Steps
1. Walk lazily: `Files.walk(root).filter(Files::isRegularFile)`.
2. Read attrs once: `Files.readAttributes(p, BasicFileAttributes.class)`.
3. Preview: read first 4KB via FileChannel, decode UTF-8 with REPORT.
4. Write index with BufferedWriter 64KB buffer, flush every 1000 rows.
5. Print stats: files/s, MB/s, p50/p99 per-file time.

## Skeleton
```java
var q = new ArrayBlockingQueue<Path>(256);
ExecutorService pool = Executors.newFixedThreadPool(Runtime.getRuntime().availableProcessors());
// producer: walk → q.put; consumers: poll → index
```

## Acceptance
- 10k files < 5s on SSD; no FD leak (`lsof` stable).
- Handles OVERFLOW/symlink cycles, bad charset without crash.
- Flags: `-Xmx512m -XX:MaxDirectMemorySize=256m`.

## Stretch
- Memory-mapped preview for >1MB files.
- WatchService incremental re-index.
- JSON output + `--grep <pattern>` mode.

## Demo Script (2 min)
1. Run on repo root, show throughput. 2. Add file, re-index incrementally.
