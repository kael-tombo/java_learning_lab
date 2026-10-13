# Debugging: JVM Tuning

## Read flags before theorizing

Every session opens with `java -XX:+PrintFlagsFinal -version` (collapse
whitespace, grep the five families: heap sizes, ratios, TLAB, compression,
caches). Quoting ergonomics from memory fails across machines; the flags
are the deployment's own testimony. Re-run inside containers — host
readings mislead where cgroup limits govern.

## Attribute pressure to its plane

Heap growth (Eden/Old pools, `gc` pause lines) versus code-cache
fullness (CodeHeap pools near 240M, compilation stopping with no GC
signal) versus Metaspace growth (Metaspace pool climbing, metadata-GC
causes). Each plane has its own MXBean and log signature; check all three
before changing any flag. The most expensive mistake here is raising
`-Xmx` for a Metaspace leak.

## Diagnose allocation paths

Suspected allocation bottleneck: run the workload with and without
`-XX:-UseTLAB` in staging (diagnostic-only, never production) and compare
— a large delta confirms allocation contention rather than GC. Production
fix direction is almost always fewer/smaller allocations or reused large
buffers, not flag changes; TLABs already make the uncontended path ~10
instructions.

## Run the one-flag trial

Form the mechanism sentence ("young pauses dominate p99; larger heap
should space them out"), pick ParallelGC for lever clarity, pin
everything except `-Xmx` (128m vs 512m), count `Pause Young (` lines in
`-Xlog:gc`. If counts move predictedly, the mechanism responds; if flat
(as under G1 adaptivity), the finding is about adaptivity, not failure.
Two flags per trial voids the result — re-run rather than reinterpret.

## Large pages and explicit GC checks

Large-page surprises: verify OS huge-page pools and privilege before
blaming the flag (inert without support). Latency spikes on demand:
search for `System.gc()` callers and confirm `DisableExplicitGC` posture;
an explicit full collection masquerades as collector pathology until the
cause token is read.
