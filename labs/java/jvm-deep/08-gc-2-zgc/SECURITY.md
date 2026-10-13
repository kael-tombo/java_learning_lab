# Security: ZGC

## Colored-pointer metadata handling

Color bits travel in references, including across JNI boundaries and into
dumps. A core file from a ZGC heap carries color state that only the
matching collector phase interprets — mishandled forensic tooling can
misresolve references. Restrict dump access as with any heap image, and
analyze ZGC dumps with version-matched tooling that understands the
current color layout rather than raw pointer arithmetic.

## Load-barrier timing surface

Barriers add data-dependent timing: healed (slow-path) loads cost more
than current-color (fast-path) loads. Code that loads attacker-influenced
reference graphs and then acts on timing (deserialization of untrusted
graphs, lazy healing of attacker-aged objects) exposes a subtle oracle
about object age and relocation state. Validate untrusted object graphs
by shape and size before traversal, and bound graph depth regardless of
collector.

## Allocation-stall DoS

Sustained allocation past the concurrent budget stalls mutators — a
throughput collapse reachable by any principal that drives allocation
rate (large uploads, unbounded batch parameters, decompression bombs).
Cap input sizes, bound decompression ratios, and chunk bursts so
allocation rate stays under concurrent drain. Monitor stall counters as
a security signal, not only a capacity one.

## Timer and log exposure

`ZCollectionInterval` values and `gc` reason tokens disclose workload
cadence (idle patterns, burst timing) to log readers. Keep GC logs out
of client-visible surfaces. The opt-in nature of ZGC (`UseZGC` on the
command line) also means launch flags are security-relevant config —
review them where you review any privilege or resource boundary.

## No zeroing guarantee

Concurrent relocation copies live data and abandons old copies without
zeroing; "collected" secrets linger until overwritten, same as under G1.
Clear key material explicitly and treat relocated-heap images as
secret-bearing.
