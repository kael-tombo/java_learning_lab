# Security: Volatile Semantics

## Threat 1 — stale-visibility bypass of safety flags
A non-volatile `shutdown/cancel/revoked` flag may never become visible to worker threads; a revoked credential keeps working. Publish every cross-thread safety decision through volatile/lock/atomic edges, and test revocation under contention.

## Threat 2 — half-published objects via broken DCL
Unsynchronized lazy singletons (config, keys, policies) can expose partially constructed security state. Demand volatile + DCL, holder idiom, or enum singleton for every lazily published security object.

## Threat 3 — torn 64-bit reads of limits/nonces
Non-volatile `long` quota/nonce/counter reads may tear (JLS 17.7 permission) into half-old values, bypassing limits. Declare them volatile or atomic; never rely on "HotSpot does not tear".

## Threat 4 — volatile-array confusion leaking stale policy entries
Policy tables behind a `volatile Entry[]` reference publish the handle, not the cells; updated rules stay invisible. Use per-element volatile semantics (AtomicXArray/VarHandle) or republish-then-swap the whole array reference.

## Checklist
- [ ] Safety flags volatile. [ ] Security singletons safely published. [ ] 64-bit security fields volatile/atomic. [ ] Policy arrays element-safe.

## Threat 5 — revocation flags that never arrive
- A non-volatile `revoked/cancelled/shutdown` flag lets a cancelled credential, revoked token, or stopped worker keep running: the JIT hoists the reader's check and the revocation never lands.
- Publish every cross-thread safety decision through a volatile write/read pair (or atomic/interrupt edge); test revocation under OSR-hot loops, not just cold unit tests.
- Log revocation-to-effect latency in drills: any outlier shaped like "never" is a missing edge, not a slow network.

## Threat 6 — half-published security singletons
- Lazy policy engines, key holders, and config singletons built on plain-field DCL can expose partially constructed security state — null ciphers, zeroed limits, permissive defaults mid-construction.
- Demand volatile-DCL, holder idiom, or enum singleton for every lazily published security object; review-gate any hand-rolled lazy init touching auth material.
- Treat "unreproducible in tests" as the signature, not an alibi: DCL races need specific JIT/CPU interleavings, so absence in CI proves nothing.

## Threat 7 — torn 64-bit security values
- Quotas, nonces, expiry timestamps, and sequence counters in plain `long`/`double` may tear (JLS 17.7 permission) into half-old values — limit checks compare against a number no thread ever wrote.
- Declare security-relevant 64-bit fields volatile or atomic; never rely on "HotSpot does not tear" — portability is the requirement, current-CPU behavior is anecdote.
- Prefer `AtomicLong` with CAS loops where the value is both checked and updated (nonce consumption, quota decrement) — visibility without atomicity still races.

## Detection
- Grep for cross-thread boolean/long flags lacking `volatile` (or atomic wrappers): each hit is a finding until a hb chain is drawn for it.
- Grep for `volatile.*\[\]` declarations: every volatile array reference is an element-visibility finding until per-element semantics are shown.
- Grep for lazy-singleton shapes (`if (x == null)` + `synchronized`): each must resolve to volatile-DCL, holder, or enum — anything else is the DCL bug.
- Include an ARM (or weak-model) run in security CI for visibility-sensitive paths; x86-only CI cannot catch missing-barrier bugs.

## Checklist additions
- [ ] Revocation/cancel flags volatile or interrupt-driven, drill-tested hot.
- [ ] Security singletons volatile-DCL / holder / enum — no plain-field lazy init.
- [ ] 64-bit security fields volatile or atomic; no tearing-permission exposure.
- [ ] Policy arrays element-safe (AtomicXArray/VarHandle) or reference-swapped whole.
- [ ] Weak-model CI run covers visibility-sensitive paths.
