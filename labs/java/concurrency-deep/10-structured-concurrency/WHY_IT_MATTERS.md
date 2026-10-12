# Why It Matters: What Scopes Buy You

## Containment by default

The block guarantees no subtask survives it. Code review stops asking
"who shuts this down?" because the answer is always the closing brace.
Leak audits shrink from whole-codebase thread hunts to checking that
work actually runs inside scopes.

## Fail-fast without machinery

One failing backend cancels its siblings and surfaces through
`throwIfFailed()` — no latch, no atomic first-error slot, no manual
cancel loop. Conjunctive fan-out (need every result) drops from dozens
of coordination lines to fork-join-throwIfFailed.

## Hedging without races in user code

`ShutdownOnSuccess` turns replica racing into fork-join-result. The
first answer wins, losers are cancelled, and no user-level race decides
which exception masks which value. Retry-and-race logic that used to
need careful `CompletableFuture.anyOf` plumbing becomes declarative.

## Cancellation that actually propagates

Policy-driven `shutdown()` interrupts every live subtask the moment the
decisive completion lands. Siblings parked in interruptible calls wake
immediately; the scope still reaps the stubborn ones at `close()`. The
window between "outcome known" and "resources freed" collapses.

## Readable fan-out

Scoped code reads like sequential code with `fork` sprinkled in: fork
handles, join once, use results. A newcomer traces one block instead of
a graph of stages, callbacks, and executors. Onboarding cost for
concurrent paths approaches that of straight-line code.

## Composable nesting

Scopes inside subtasks give divide-and-conquer (lab 07's recursive
shapes) failure propagation and containment the raw pool never had.
Each level's `throwIfFailed()` converts child failure into the parent's
unit of failure, so deep trees report coherently instead of partially.

## Enforcement over convention

Ownership and binding rules throw (`WrongThreadException`,
`IllegalStateException`, `StructureViolationException`) instead of
documenting wishes. Misuse fails loudly at the call site rather than
corrupting results three methods away, which shortens debugging from
hours to minutes.

## A stable core under a moving surface

Preview syntax will keep shifting until finalization (JEP 505 reshaped
parts after this lab's JDK 23 pin), but the five invariants — lexical
containment, owner-only control, two policies, three subtask states,
thread-per-subtask on virtual threads — carry across releases.
Learning them pays off on every JDK from 21 onward.
