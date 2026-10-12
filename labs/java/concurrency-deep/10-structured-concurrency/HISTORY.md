# History: Structured Concurrency in the JDK

## Incubation: JDK 19, JEP 428

Structured concurrency first shipped as an incubator API in JDK 19 under
JEP 428. Incubator status meant the API rode alongside incubating
virtual threads and scoped values — the three efforts were co-designed,
with bindings propagating lexically into subtasks from the start.

## Incubation: JDK 20, JEP 437

JDK 20 carried the second incubator round as JEP 437. The core shape —
scope owns subtasks, `fork`/`join`/`close`, fail-fast and first-success
policies — stabilized here while feedback accumulated on nesting,
cancellation, and the policy extension point.

## First preview: JDK 21, JEP 453

JDK 21 promoted the API to preview under JEP 453. Preview status wired
it into `javac --release 21 --enable-preview` compilation and required
explicit opt-in at both compile and run time, signalling that syntax
could still move even as the containment concepts held steady.

## JDK 22-24: successive preview rounds

The API remained in preview across JDK 22, 23, and 24 with revisions to
method shapes and failure-reporting details. Code written against one
release's surface may need re-verification on the next — the ownership
rules and the two-policy split survived, while signatures shifted.

## This lab's pin: JDK 23

All runnable snippets here target the JDK 23 preview surface, built with
`javac --release 23 --enable-preview` and run with `java
--enable-preview`. Pinning matters because the next revision moved
pieces again; a snippet verified on 23 should be re-checked, not
assumed, on later releases.

## Fifth preview: JDK 25, JEP 505

JEP 505 took structured concurrency to a fifth preview in JDK 25 and
reshaped parts of the API — still not final. The direction confirms the
model (lexical ownership, policy-driven shutdown, composable nesting)
while the spelling continues to evolve toward eventual standardization.

## What stayed constant through every round

Lexical containment (nothing escapes `close()`), owner-only
join/close/result, fail-fast versus first-success policies, subtask
states (`UNAVAILABLE`/`SUCCESS`/`FAILED`), and thread-per-subtask on
virtual threads. Six releases changed the surface; none changed these
five invariants, which is why this lab teaches invariants first.
