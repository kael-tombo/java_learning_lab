# Security: CopyOnWriteArrayList

## Write-amplification DoS

Each write copies n references. A low-privilege actor able to trigger
writes (registrations, config updates, list appends) on a large COW list
multiplies input bytes ~8n× into allocation — asymmetric resource burn.
Mitigations: authenticate/rate-limit mutation endpoints, cap list size,
prefer O(1)-write structures for user-influenced growth.

## Stale-snapshot decisions

Snapshot iterators/reads see construction-time state: an allowlist check
iterating a stale snapshot admits recently-revoked entries until the
iterator is re-acquired. Security decisions must sample `getArray()`
fresh per decision (new iterator / indexed read), never reuse a
long-held one across a policy change.

## Iterator pinning as retention DoS

An attacker holding iterators (e.g. open streaming reads) pins full array
versions across all subsequent writes — memory grows with write count
while the API looks idle. Bound iterator lifetimes; materialize and close.

## In-place element mutation

Mutating a published element's fields sidesteps happens-before per field:
readers see torn/uneven field states with no ordering guarantee. For
security-sensitive payloads (permissions, tokens) publish new immutable
element objects rather than mutating shared ones.

## External-locking illusion

`synchronized (cowList)` around compound checks excludes nothing (writers
use the internal lock). TOCTOU behind client-side locking gives false
safety — e.g. size-check-then-act admitting over capacity. Use the atomic
methods (`addIfAbsent`) or re-validate after acting.
