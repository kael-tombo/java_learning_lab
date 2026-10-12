# Phaser — Math Foundation

## Advance condition as a counting invariant

For phase k let R(k) be registered parties and A(k) arrivals recorded.
Phase k completes if and only if A(k) = R(k) (or termination is forced).
Registration mutates R(k) upward mid-phase (adding equally to unarrived),
deregistration mutates it downward while contributing its arrival — so the
invariant is maintained dynamically rather than fixed at construction, the
formal difference from `CyclicBarrier` (constant R) and `CountDownLatch`
(monotone countdown to zero, one phase).

## Await semantics as inequality

`awaitAdvance(p)` blocks while `current == p` and returns when
`current != p`. Since phases advance monotonically (modulo wraparound),
`current != p` after waiting from `p` means `current > p` in phase order:
the caller provably slept through the advance of p. A stale `p` sampled
from `getPhase()` breaks the proof — `current != p` may already hold at
call time, returning without witnessing any advance. Only `p` from your
own `arrive()` carries the guarantee that you were counted in it.

## Return-value arithmetic

Arriving during phase k: `arrive()` yields k; the subsequent advance
publishes k+1, which is what `arriveAndAwaitAdvance()` and a correctly
paired `awaitAdvance(k)` observe. Off-by-one confusion between the two
returns is the most common phaser bug — formally, one names the phase
arrived-into, the other the phase released-into.

## Tiering depth

With fan-out f (parties per node) and N total parties, tree depth is
log_f(N) and each phase costs that many sequential coordination hops.
Single-level (depth 1) minimizes latency; tiering minimizes per-node
contention. Break-even is workload-measured, but the scaling law is exact:
contention per node drops by factor f per added level while latency grows
additively by one hop.

## Overflow bound

Phases are signed 32-bit: after 2^31 advances the count wraps to negative,
which the phaser reads as termination. At one phase per microsecond that
is ~36 minutes per 2^31... recompute: 2^31 us ~= 2147 s ~= 36 min. At one
phase per millisecond it is ~25 days; per second, ~68 years. Only hot
spin-phased loops approach the bound — hence "documented, not feared" —
but any `phase < 0` guard must distinguish wrap from real termination by
checking `isTerminated()` alongside expected phase counts.

## Termination as a fixed point

Default `onAdvance` terminates exactly when R = 0 after an advance: the
empty rendezvous is the fixed point. Custom predicates terminate at
whatever (phase, parties) set they accept; monotonic predicates
(`phase >= K`) guarantee termination within K phases regardless of party
dynamics, which is why phase-bounded overrides are the safe default shape.
