# Reflection: Final Field Semantics

## What the freeze changed in your mental model

Before this lab, how did you assume an object became visible to other
threads — and did that picture distinguish the reference race from the
field visibility? State in one paragraph what JLS 17.5 adds: which reads
are guaranteed, and through which chains.

## Your constructors under audit

Pick a constructor you have written that registers, publishes, or starts
something. Walk it line by line: does every publication happen after
every final store? If not, sketch the reordered version (store first,
publish last or in a factory) and name the early reader that the old
order exposed.

## Theorem vs weather in your test suite

Recall a concurrency test that "passes green" on your machine. After the
mutable-twin lesson, what would it take to promote that green run from
weather to theorem — which specification clause, which chain of links?
If none exists, what does the green run actually license?

## The transitive trap you almost set

Describe a case where you shared (or nearly shared) a `final` reference
to mutable contents — a record wrapping a list, an array stored without
copying. Which side of the reference/contents boundary did your
reasoning stop at, and what copy or immutable snapshot fixes it?

## String as evidence

`String` crosses threads unsynchronized in every Java program via
`final value` + `final coder`. How does that everyday fact reshape your
sense of where "synchronization" lives — must every shared object pay
per-read ordering, or can construction alone carry it?

## What you will enforce

Name one constructor discipline you will now treat as non-negotiable
(no `this` escape, no overridable call, defensive copy, final-ify
snapshots) and the code review check that enforces it.
