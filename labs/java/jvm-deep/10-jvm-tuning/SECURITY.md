# Security: JVM Tuning

## Heap dumps are secret stores

Tuning artifacts (heap dumps, JFR recordings, `gc*` logs with sizing)
capture live secrets, reference graphs, and capacity intelligence. The
TLAB win means secrets scatter across per-thread buffers rather than one
arena — a dump still collects them all. Restrict dump creation and
retention, encrypt at rest, and clear key material (`Arrays.fill`,
direct-buffer zeroing) instead of relying on collection timing.

## Explicit GC as a latency weapon

`System.gc()` without `ExplicitGCInvokesConcurrent` forces a full STW
collection — a caller-triggered latency spike. Plugin, scripting, or
multi-tenant paths that reach it hand untrusted principals a pause
button. Run `-XX:+DisableExplicitGC` where such paths exist, audit the
remaining explicit-GC surface, and alert on full-GC cause tokens naming
explicit invocation.

## Large pages and memory locking

Huge pages plus lock-memory privilege pin memory against swapping — a
deliberate denial of the OS's pressure relief. Over-reserved huge-page
pools starve co-tenants; under-provisioned ones make the flag inert while
operators believe they tuned. Size pools from measured heap plus margin,
review privilege grants as security boundaries, and verify pool use
rather than flag presence.

## Flag integrity across environments

Collector, heap, and compression flags reshape performance and DoS
posture wholesale (`-Xmx36g` silently dropping compressed oops changes
footprint; collector swaps change pause classes). Treat launch flags as
security-relevant config: pin base images, review flag diffs like code
diffs, and assert posture in CI (`PrintFlagsFinal` reads for the flags
that matter) rather than trusting scripts.

## Log exposure discipline

GC and flag logs disclose heap sizes, pause behavior, region geometry,
and workload cadence — reconnaissance for allocation-based DoS (humongous
churn, burst sizing). Keep tuning logs out of client-visible surfaces and
bound their retention like any capacity intelligence.
