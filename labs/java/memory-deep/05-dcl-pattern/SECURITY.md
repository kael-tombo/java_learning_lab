# Security: DCL Pattern

## Half-constructed singletons as trust hazards

Security singletons (policy engines, key holders, auth directories)
built through keyword-less DCL can hand a racer a half-constructed
instance: default policy, null keys, fail-open state — legally, under
the old reorder. The `volatile` keyword on a security singleton is not
style; it is the edge that orders authorization state before the
reference that grants access to it.

## Double initialization and side-effect doubling

Recheck-less DCL runs security constructors twice: double audit-log
entries, double key generation (first key silently discarded — where did
it go?), double registration with divergent state. For singletons whose
construction has side effects beyond memory (keygen, enrollment,
licensing), `constructions == 2` is a security event, not a benign
duplicate. The locked recheck is the control.

## Publication of security singletons: prefer the holder

The holder idiom removes both hazards structurally: JVM-locked,
exactly-once init under JLS 12.4.2, with no keyword to forget and no
recheck to drop. Security singletons should justify DCL over the holder
in writing; "we always use DCL" is not a justification.

## Serialization forks of security identity

A DCL/holder security singleton without `readResolve` deserializes into
a second instance with its own (possibly defaulted or replayed) state —
two policy engines, two key stores, divergent enforcement. Use the enum
form (JVM identity across deserialize, reflection-proof) or add
`readResolve` returning the canonical instance, and test the round-trip
identity assertion from this lab.

## Reflection against singletons

`Constructor.setAccessible` plus `newInstance` forks plain (DCL/holder)
singletons into ungoverned twins; enums throw instead. Where singleton
identity is a security boundary (one policy source, one key custodian),
the enum's reflection immunity is a functional requirement, and
module-access closure (`opens`/`setAccessible` policy) is defense in
depth.

## Review checklist

- Security singleton: holder or enum unless parameters force DCL.
- DCL instances: volatile field, canonical monitor, locked recheck,
  Bloch local — all four, verified literally.
- Serialization round-trip preserves identity (test it).
- Construction side effects audited for double-run consequences.
