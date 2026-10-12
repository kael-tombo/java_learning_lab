# References: Structured Concurrency

## JEP 428 — Structured Concurrency (Incubator, JDK 19)

First incubator delivery of `StructuredTaskScope` alongside virtual
threads and scoped values. Establishes lexical ownership, fork/join
structure, and the two-policy split in prototype form.

## JEP 437 — Structured Concurrency (Second Incubator, JDK 20)

Second incubator round. Stabilizes the containment core and the
`handleComplete` extension point while collecting feedback on nesting
and cancellation behavior.

## JEP 453 — Structured Concurrency (Preview, JDK 21)

First preview promotion. Puts the API behind `--enable-preview` /
`--release 21`, signalling concept stability with syntax still allowed
to move in later rounds.

## JDK 22–24 preview revisions (same API line)

Successive preview rounds revising method shapes and failure reporting
on the way to the fifth preview. This lab pins runnable code to the
JDK 23 surface within that line and re-verifies rather than assumes
across releases.

## JEP 505 — Structured Concurrency (Fifth Preview, JDK 25)

Fifth preview round, still not final. Reshaped parts of the API after
the JDK 23 surface documented here — consult it before porting any
snippet forward.

## OpenJDK source: java.util.concurrent.StructuredTaskScope (JDK 23)

Authoritative enforcement reference: owner checks throwing
`WrongThreadException`, fork-after-close `IllegalStateException`,
binding-mismatch `StructureViolationException`, subtask states
`UNAVAILABLE`/`SUCCESS`/`FAILED`, and the `handleComplete` dispatch.
Read the JDK 23 tree specifically; later trees reflect JEP 505 drift.

## How to cite preview code correctly

Name the JDK release, the `--release`/`--enable-preview` flags used,
and the JEP surface (here: JDK 23, pre-JEP-505). Never present preview
spelling as final API — pin, flag, and re-verify.
