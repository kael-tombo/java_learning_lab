# EXERCISES — NIO Channels

## 1. The missing `flip()` (beginner)
Delete one `flip()` in `scatterRead` and run `main`. Record which assert
fails and what the buffer state (`position/limit/remaining`) is at that
point. Restore and explain why no exception was thrown.

## 2. Stale-tail bug (beginner)
Remove `TRUNCATE_EXISTING` from `writeFile`, write a 20-byte string then a
5-byte string to the same path, and read back. Explain the 15 trailing
bytes. When is *appending* (no truncate) actually what you want?

## 3. Scatter a structured message (intermediate)
Write a 12-byte header + variable body + 4-byte CRC to a file. Read it back
with `scatterRead(path, 12, bodyLen, 4)` and verify the CRC. What happens
when the file is shorter than 12+bodyLen+4?

## 4. Map-in-a-loop leak (intermediate)
Call `memoryMappedWrite` 10,000 times on Windows and watch handles/pages
(e.g. Process Explorer or `Get-Process | Select Handles`). Then add
`Unsafe.invokeCleaner` unmapping (see `07-file-io`'s `EliteFileIOTraining`)
and re-measure. Relate to the deep-dive guide.

## 5. `transferTo` vs copy loop (advanced)
Copy a 500 MB file via `transferTo` and via `bufferedCopy`-style loop.
Compare wall time and CPU time (`ThreadMXBean.getCurrentThreadCpuTime`).
Check the return value of `transferTo` — under what conditions is it
short, and how must callers loop?
