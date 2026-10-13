# Security: G1 GC

## Heap inspection after collection

Evacuation copies live objects and abandons dead ones in place — it does
not zero them. A heap dump or core file can containnominally "collected"
secrets (tokens, keys) lingering in freed regions until overwritten.
Clear secret arrays explicitly (`Arrays.fill`) when done, and treat dumps
from G1 heaps as secret-bearing artifacts with the same handling as live
memory.

## Humongous regions as a DoS surface

Any principal that controls allocation sizes controls humongous demand:
repeated multi-MB allocations on small regions fragment the old set and
force full GCs (throughput collapse, long STW pauses). Cap request and
upload sizes before they reach the allocator, pool large buffers, and
alert on `gc+humongous=debug` volume — it is the early signal of this
abuse shape.

## Log and MXBean exposure

GC logs record heap sizes, pause times, region sizes, and worker counts
— capacity intelligence useful to an attacker planning allocation-based
DoS. Restrict log retention and access; do not ship `gc+init` output to
client-visible error pages. MXBean pool names (`G1 Eden Space`, ...)
disclose collector choice — harmless internally, unnecessary externally.

## Explicit GC abuse

`System.gc()` without `ExplicitGCInvokesConcurrent` forces a full STW
collection — a latency spike on demand. Untrusted code paths (plugins,
scripted extensions) must not reach `System.gc()`; run with
`-XX:+DisableExplicitGC` where such paths exist, and audit the one flag
that re-enables concurrent behavior before relying on it.

## SATB floating garbage and secrecy lifetime

Floating garbage retains dead objects one extra cycle by design. Secrets
that "should" die at marking time survive until the next cleanup. For
high-sensitivity material prefer off-heap or explicitly cleared buffers
over relying on collection timing to erase anything.
