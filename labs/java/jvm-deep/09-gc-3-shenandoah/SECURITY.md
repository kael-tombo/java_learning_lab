# Security: Shenandoah GC

## Forwarder as an extra attack surface word [JEP]

Every object carries a Brooks word that decides which copy is live. A
memory-safety bug that corrupts the forwarder redirects all subsequent
reads through the barrier to attacker-chosen memory — a stronger
primitive than corrupting one data field. Harden exactly as for any GC
metadata: no unchecked unsafe writes near object headers, bounds-check
untrusted indexing before it reaches object access, and treat forwarder
integrity as part of the memory-safety boundary on shipping builds.

## Read-barrier timing [JEP]

Through-forwarder reads cost differently when the forwarder already points
at the current copy versus when healing intervenes. Secret-dependent
access patterns that straddle evacuation (reads of attacker-aged objects
during concurrent moves) expose timing deltas about object age and copy
state. Validate untrusted graphs by shape and depth before traversal, and
keep secret handling off attacker-influenced reference paths regardless
of collector.

## Uncommit and secret lifetime [JEP]

`ShenandoahUncommit` returns idle regions to the OS after the 5-minute
delay — but "returned" is not "zeroed" from the application's view, and
recommitted regions may still expose stale bytes to heap readers before
overwrite. Clear key material explicitly (`Arrays.fill`, direct-buffer
zeroing) rather than relying on collection or uncommit timing. Treat
uncommitted-then-recommitted windows as secret-bearing until proven
overwritten.

## Availability-gated config [measured]

Collector selection is a launch-flag branch with a refusal mode ("not
supported", nonzero exit). An attacker or misconfiguration that flips the
flag changes pause behavior and denial-of-service posture wholesale
(STW evacuation vs concurrent). Pin base images, assert the flag surface
in CI (1-vs-many count), and review collector flags with the same rigor
as any resource or privilege boundary.

## Log and MXBean exposure [reported]

Phase names (`Pause Init Mark`, `Concurrent evacuation`) and MXBean names
(`Shenandoah Cycles`/`Pauses`) disclose collector choice and workload
cadence to log readers. Keep `gc` logs out of client-visible surfaces,
as with every collector in this module.
