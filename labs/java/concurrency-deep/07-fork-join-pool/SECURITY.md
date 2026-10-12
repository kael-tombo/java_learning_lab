# Security: Fork-Join Pool

## Common-pool contention as DoS

Any tenant that runs blocking or explosive-fan-out work on the common pool
degrades parallel streams and CF chains JVM-wide — a shared-resource DoS with
no privilege required. Defenses: never run untrusted-lambda recursion on the
common pool; give untrusted/IO work bounded private pools; `orTimeout` + queue
limits on every external-facing fork.

## Task-explosion abuse

Recursive tasks with attacker-influenced split depth (tiny threshold over
attacker-sized input) allocate millions of task objects — heap exhaustion via
`2n/t` arithmetic. Defenses: clamp input size before forking; floor the
threshold (never below the ~1µs-leaf mapping); cap parallelism for untrusted
shapes (`MAX_CAP` is 32767 — the real cap must be yours).

## Blocking without compensation as liveness attack

Attacker-paced latches/sockets inside `compute()` park workers that read as
busy — effective parallelism decays with no error. Require `ManagedBlocker`
(or off-pool execution) for any block reachable by external timing; monitor
`getPoolSize()` vs `getParallelism()` divergence as a health signal.

## Exception exfiltration

`join()`/`invoke()` rethrow task exceptions to the joining thread — a failing
task can surface internal paths or backend details to an untrusted joiner.
Sanitize at task boundaries (`handle`-style wrapping into typed errors) the
same way CF pipelines do.

## Pool-leak persistence

Leaked non-daemon FJ pools keep threads (and their context classloaders)
alive past redeploy — a redeploy-leak DoS in containers. Mandate
try-with-resources (19+) or `shutdown` + `awaitTermination` in finally for
every non-common pool; never expose pool creation to untrusted callers.

## Property-override integrity

`common.parallelism` / `common.threadFactory` are startup properties —
attacker-controlled JVM flags resize the shared pool for every borrower.
Treat launch flags as security-sensitive config; assert
`commonPool().getParallelism()` at startup in hardened deployments.

## Checklist

- [ ] No untrusted/blocking work on the common pool
- [ ] Input-size clamps + threshold floors on recursive tasks
- [ ] `ManagedBlocker` on externally-paced blocks
- [ ] Task exceptions sanitized at join boundaries
- [ ] Every private pool try-with-resources or shutdown/finally
- [ ] Startup assertion on common-pool parallelism
