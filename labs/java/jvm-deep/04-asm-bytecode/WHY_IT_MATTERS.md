# Why It Matters: Bytecode Generation

## Production runs on generated classes

Spring proxies, Hibernate lazy entities, Mockito mocks, ByteBuddy
agents, lambda adapters — nearly every Java service executes classes
no source file produced. Engineers who understand parse→transform→
emit read those frameworks' failure modes (proxy `VerifyError`,
mock linkage errors, agent-redefined frames) as builder-level facts
instead of magic. This lab's five probes are that literacy in
runnable form.

## The operation graph outlives any library

ASM method names will age; JEP 457/466 preview signatures will
finalize and shift. Parse→inspect→transform→emit, withhold-to-delete,
derived frames, and labels-over-offsets survive both — they are the
stable half. Learning the graph against today's verifiable API
ports directly to tomorrow's finalized one and backward to any ASM
codebase you inherit.

## Derivation kills a bug class

Hand-computed `max_stack` and `StackMapTable` frames caused a
generation-long history of `VerifyError`s that only reproduced on
specific branch shapes. Builders that track types at emit time
remove the class: if the instruction graph is consistent, the frames
are correct. Teams choosing generation tooling should weight this
above API familiarity — the cheapest frame bug is the unrepresentable one.

## Transforms are deploy-time power tools

Method-dropping (dead-code stripping), call-site rewriting (API
migration), probe injection (tracing), reference renaming (shading):
each is a 10-line transform lambda with the passthrough preserving
everything unmentioned (`NestHost`, `Record`, debug tables). Compared
against fork-and-patch of dependencies, transforms are smaller,
reviewable, and testable through re-parse assertions.

## Verification keeps generation honest

Because `defineClass` enforces the same gates as `javac` output,
generated code carries no second-class risk: identical JIT paths,
identical inline caches, identical failure loudness. The discipline
this enables — test emitters through define-plus-invoke, assert
listings, pin the preview rig in CI — turns bytecode work from
folklore into ordinary engineering with stack traces.
