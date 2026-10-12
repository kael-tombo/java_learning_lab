# StampedLock — Why It Matters

## Read-mostly workloads dominate servers

Caches, routing tables, live configuration, game-entity positions, metrics
snapshots: written occasionally, read thousands of times per second. Under a
classic read-write lock each of those reads performs a CAS on one shared
word, so reader threads serialize on the cache-coherence protocol instead of
on the data. StampedLock's optimistic path removes readers from shared state
entirely — the read path scales with core count until writers actually
collide with it.

## Correctness users feel

- **Torn-snapshot protection done once, reused everywhere.** The
  sample-copy-validate idiom (e.g., reading an (x, y) point atomically) is a
  reusable shape for any multi-field invariant. Learn it here, apply it to
  every lock-free-ish read path.
- **Upgrade without deadlock.** Workflows that inspect-then-mutate (cache
  miss handling, lazy initialization, copy-on-write checks) get a real
  conditional upgrade instead of the release-reacquire window.
- **Explicit failure signals.** Conversion returns 0; validation returns
  false. Both force the caller to handle contention visibly, which surfaces
  retry policy in code review instead of hiding it in queue behavior.

## Where it does not matter

Write-heavy counters, long analytical scans, and any path that performs I/O
or calls alien code mid-read gain nothing — validation fails too often, the
window is too wide, or reentrancy is required. Recognizing those shapes and
reaching for `ReentrantLock`/`synchronized` instead is the actual skill.

## Interview and code-review signal

Senior reviewers look for four things: validate-before-act ordering,
side-effect-free optimistic bodies, the mandatory conversion fallback, and
no re-acquire under hold. Getting those right in a StampedLock review
demonstrates understanding of version-based concurrency generally —
optimistic concurrency control in databases, sequence locks in kernels, and
epoch schemes all rhyme with sample-then-validate.

## Operational payoff

Fewer CAS storms means lower tail latency on read endpoints and less
coherence traffic on multi-socket machines. The win shows up as flatter
p99 under reader fan-out, measurable with the harness in PERFORMANCE.md.
