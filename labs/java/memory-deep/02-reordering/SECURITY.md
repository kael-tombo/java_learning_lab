# Security: Reordering

## Threat 1: racy double-checks fail open

A publication check like `if (initialized) use(config)` on plain
fields can observe the flag early (StoreLoad/StoreStore escape on weak
hardware) and consume a half-built policy object — fail-open by
reordering rather than by logic. Security gates must sit behind edges
(volatile flag, latch, lock): the check and the use share one ordered
region (roach-motel semantics, lab 03), never a plain race.

## Threat 2: "works on x86" as a security argument

Plain message-passing passes 2000/2000 on x86 (lab 03 snippet 4) and
fails elsewhere: StoreStore is preserved on TSO, freed on ARM. Any
safety case resting on x86-only testing (policy publish, revocation
broadcast, key rotation) is untested on the deployment hardware it
will eventually meet. Require edge-based verdicts (volatile/latch 0
anomalies everywhere), not x86 rate anecdotes.

## Threat 3: timing mitigations are not mitigations

Inserting delays, retries, or sleeps around a racy check (the
`parkNanos` pattern of snippet 3) suppresses exploitation probability
on one machine while leaving the race — and the exploit — intact.
An attacker who controls load and timing (colocated tenants,
request bursts) manufactures the overlap the defender's quiet lab
never saw. Only edges change the verdict; timing changes the rate, in
the attacker's favor under pressure.

## Threat 4: release/acquire where total order is required

Using `setRelease`/`getAcquire` for mutual-observation protocols
(two-sided readiness, paired capability checks) leaves 61-90%
anomaly rates an attacker can harvest: each chain holds while the
cross observation slips through. Reserve release/acquire for
one-directional handoff chains (sequence numbers, pipelines);
mutual gates need full volatile (StoreLoad fenced both sides) or a
lock. Match the mode to the shape — "cheaper ordering" is not
"enough ordering."

## Threat 5: litmus-blind review of lock scope

A monitor that covers stores but not their paired loads (half-wrapped
Dekker) still races: exclusion covers the critical section only.
Review every security-critical pair (publish+check, flag+data,
grant+use) for *complete* enclosure — the `MonitorFix` shape (whole
pair inside one lock) is the template, partial wrapping is the finding.

## Review checklist for reordering-sensitive gates

- Every gate flag is volatile (or latched/locked) — no plain check
  guards security state on any platform.
- No sleep/retry/drain stands in for an edge; each has a named hb
  rule cited beside it.
- Mutual-observation shapes use volatile-both-sides or one lock —
  release/acquire appears only in one-directional chains.
- Litmus-sensitive code carries its rendezvoused test (20000-round
  driver, verdict assertions) so regressions print nonzero instead of
  whispering.
