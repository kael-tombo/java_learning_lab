# Security: JMM Foundations

## Threat 1: unsafe publication of security state

Publishing an auth config, allowlist, or crypto parameter object
through a plain reference lets a reader observe default (zero/null) or
half-constructed fields — potentially an open policy or a null key that
fails open. The `LatchEdge` shape (graph writes -> countDown -> await ->
reads) is the minimum for security-critical publication; a volatile
reference or final-field safe publication also suffices. Plain-flag
publication of policy objects is a vulnerability, not a style issue.

## Threat 2: stale revocation checks

A reader caching `isRevoked` or `isBlocked` in a plain field may never
observe revocation: the JIT hoists the check out of the loop and the
CPU serves the stale line indefinitely. Revocation flags must be
volatile (or checked under a lock / via an atomic): visibility *is* the
security property. Any "eventually an attacker gets more tries" gap
caused by a missing edge is an exposure window with no upper bound.

## Threat 3: racy counters and limiters

Rate limiters, retry budgets, and nonce/sequence generators built on
plain or volatile increments lose updates under contention (the lab's
volatile++ contrast: millions lost at 2M scale). Lost increments mean
more attempts granted than policy allows. Limiters need atomics or
locks — the `LockEdge` verdict (exactly 2000000) is the acceptance
criterion shape for any counting enforcement.

## Threat 4: causality does not save validation

Causality guarantees values came from somewhere — including attacker
controlled somewhere. A racy reader validating `index` against
`[0, 100000]` still faces TOCTOU: the value may change between check
and use with no edge constraining it. Validate *and* consume under the
same edge (re-read under lock, or transfer through a handoff), never
check-then-use across an unordered gap.

## Threat 5: library-edge trust boundaries

Hand-rolled ready flags at trust boundaries (plugin init, policy load,
key rotation) fail exactly where review is thinnest. Prefer specified
edges (`CountDownLatch`, `Future`, queue handoff) whose hb semantics
are documented and stable across JDKs — hand-rolled protocols inherit
every JIT/CPU subtlety of lab 02 with none of the specification cover.

## Review checklist for security-sensitive handoffs

- Every policy/config/key object crosses threads through a named edge
  (volatile reference, latch, future, lock) — never a plain store.
- Every revocation/enforcement flag is volatile or atomic — prove the
  reader cannot hoist it by pointing at the edge.
- Every counting enforcement totals exactly under concurrency test
  (LockEdge-style oracle: expected vs observed, looped).
- No check-then-act spans an unordered gap; validation and use share
  one critical section or one handoff edge.
