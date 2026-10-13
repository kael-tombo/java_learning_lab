# Flashcards: ZGC

Q: How is ZGC selected, and what is on by default?
A: Opt-in with `-XX:+UseZGC`; generational mode (`ZGenerational=true`) is
the default on the measured JDK 23.

Q: Where does ZGC keep GC metadata, and what checks it?
A: Color bits in each reference; a load barrier on every reference load
checks color and heals stale references via the slow path.

Q: What stops the world in ZGC, and how long does it take here?
A: Only mark-start, mark-end, and relocate-start handshakes; measured
0.010-0.026 ms each (asserted <1 ms).

Q: What do lowercase `y` vs uppercase `Y`/`O` prefixes mean?
A: `y` = young-only minor work; `Y`/`O` = young/old phases of a major.

Q: Name the four ZGC collectors and two pools.
A: Collectors `ZGC Minor/Major Cycles` + `ZGC Minor/Major Pauses`; pools
`ZGC Young Generation` and `ZGC Old Generation`.

Q: What are the five collection reasons seen in logs?
A: `(Warmup)` (always first), `(Allocation Rate)`, `(High Usage)`,
`(Timer)`, plus explicit `(System.gc)`/`(Metadata)`/`(Clear Soft
References)`.

Q: What is `ZCollectionInterval` and its default?
A: Seconds between periodic majors; default 0.0 = off. Only enabled runs
collect idle heaps (verified: 0.1 s gave majors every ~120 ms).

Q: What is the JEP trail for ZGC?
A: JEP 333 experimental (11), JEP 377 production (15), JEP 439
generational (21).

Q: What is ZGC's throughput tax?
A: A few instructions per load (always-on barrier) plus concurrent worker
CPU — typically single-digit percent on allocation-heavy shapes.

Q: What is an allocation stall, and what causes it?
A: Mutators blocked because allocation outran concurrent relocation;
caused by sustained allocation past the concurrent budget on a tight heap.

Q: How do `-Xlog` tags join, and what breaks with commas?
A: Join with `+` (`-Xlog:gc+phases`); commas parse as separate selections
and drop the phase detail.

Q: How do cycle totals differ from pauses in the log?
A: Totals (`0.009s`) span concurrent work in seconds; pauses are `Pause
... Xms` phase lines in microseconds. Never sum or confuse them.
