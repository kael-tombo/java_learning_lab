# Security: Memory Barriers

## Threat 1: accidental publication of policy and keys

Plain reference publication of allowlists, configs, or key material
(snippet-4 shape: 0/2000 on x86, race everywhere) exposes half-built
state exactly when rollout traffic peaks — fail-open reads of default
or partially constructed policy. Security publication needs a named
release (volatile reference, latch, future): one StoreStore-backed
fence per graph, reviewed as a verdict rather than a test log.

## Threat 2: guard-flag reordering past data (the motel's open side)

A plain guard (`authorized`, `sealed`, `revoked`) lets protected
operations drift *before* the check into the region from below
(release-side drift) or lets stale data drift past an acquire — the
motel admits plain traffic by design. Guards and their guarded data
must share one ordered region (volatile guard + acquire reads, or one
lock): check and use inside the same fence scope, never straddling an
unordered gap (TOCTOU by reordering, not just by scheduling).

## Threat 3: release-grade chains guarding mutual gates

Two-sided security gates (paired approvals, mutual readiness, bilateral
capability exchange) built on release/acquire retain 61-90% Dekker
anomalies — each direction chains while the cross slips through. An
adversary that times both sides harvests the uncomposed middle. Mutual
gates need SC (volatile both sides, StoreLoad fenced) or a lock; audit
every "cheaper ordering" substitution at a gate for the pairwise-vs-total
confusion, with snippet 5 cited in the finding.

## Threat 4: opaque where ordering enforces

Routing authorization decisions through opaque (or plain) state gives
atomicity without order: the decision may pair with the wrong data
generation (no LoadLoad/StoreStore), indefinitely. Opaque belongs to
telemetry (attempt counts, statistics); enforcement belongs to
release-or-stronger with the guarded data inside the region. Any
`getOpaque`-guarded branch on security state is a finding on sight.

## Threat 5: fence-priced denial of wallet (and patience)

Blanket-volatilizing hot paths (~10 ns/store vs ~1.3 ns release)
multiplies tail latency at scale without improving verdicts — and
latency pressure is itself a security surface (timeouts failing open,
retries amplifying). Price ordering per shape (release for chains, SC
for gates, latch for one-shots) so the security budget buys verdicts
instead of heat. The ladder is a cost-control instrument, not trivia.

## Review checklist for barrier-sensitive security code

- Every policy/key/config graph crosses threads under one release
  (volatile reference, latch, future) — cite the edge, not the log.
- Every guard flag is volatile-or-stronger with guarded data inside
  the same region — no plain check guards security state anywhere.
- No mutual gate runs on release/acquire or opaque — SC or lock, with
  the 61-90% figure quoted back at proposers of downgrades.
- Timing evidence (drains, sleeps, green runs) is inadmissible for
  ordering claims; verdict tests (2000/20000 rounds, zero/nonzero)
  accompany every gate change.
