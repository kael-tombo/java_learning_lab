# Architecture: DCL Pattern

## Where DCL sits among singleton strategies

| Idiom | Lazy? | Cost | Correctness basis |
|---|---|---|---|
| `volatile` DCL | yes | 1 volatile read/call | volatile write/read edges + monitor |
| Static holder | yes | 0 (one-time class-init lock) | JLS 12.4.2 exactly-once init |
| Enum (`INSTANCE`) | no (eager) | 0 | class init + JVM serialization/reflection rules |
| `synchronized` accessor | yes | monitor/call | monitor edges |

DCL is the residual choice: laziness with constructor parameters,
non-static scope, or framework constraints that block the holder. In
every other case the holder (lazy) or enum (eager) dominates on clarity.

## The three load-bearing elements

Remove one element, lose one property — observably or by proof:

- `volatile` field: construction-before-publication ordering. Without
  it, allocate-then-publish may reorder (pre-2004 bug, alive whenever
  the keyword is deleted).
- Outer check: the fast path. Without it the pattern is just a locked
  accessor with extra steps.
- Locked recheck: exactly-once initialization. Without it, two racers
  that both observed null serialize and both construct
  (`constructions == 2` in this lab's deterministic demo).

Architecture review of any DCL instance checks all three, plus the
Bloch local-variable shape (single volatile read into `h`).

## Why the holder wins structurally

JLS 12.4.2 gives the holder a recursive, thread-safe, exactly-once
class-initialization lock owned by the JVM: first active use of
`LazyHolder` initializes `INSTANCE` under that lock, lazily, with no
user-level ordering to get wrong. DCL reimplements a weaker version of
that lock by hand. Prefer the JVM's lock to your own.

## Enum placement

The enum singleton is eager (initialized at enum-class init) but immune
to the two classic singleton killers at once: reflection
(`Constructor.newInstance` on enums throws) and serialization (the JVM
guarantees identity, no `readResolve` needed). DCL and holder both need
explicit `readResolve` for the second property.

## Cost framing, honestly held

One volatile read (~1 ns framing from lab 03) vs one uncontended
monitor pair (~20 ns). DCL pays for itself only at high call rates
(millions/second/thread); below that the synchronized accessor's
obvious correctness wins. No benchmark in this lab asserts a crossover
— hardware moves it. Frame the choice structurally (fence vs monitor),
not as a fixed threshold.

## Takeaway

Default to holder (lazy) or enum (eager + serialization-safe); use
synchronized accessors where call rates are low; reserve volatile DCL
for parameterized laziness — and then demand all three elements plus the
local-variable shape in review.
