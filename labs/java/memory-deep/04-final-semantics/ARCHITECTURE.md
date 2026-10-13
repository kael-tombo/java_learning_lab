# Architecture: Final Field Semantics

## Where the freeze sits in the memory model

The freeze is a constructor-end ordering point, not a lock and not a
fence on the read path. Architecturally it belongs with publication:
every safe-publication strategy (volatile reference, lock handoff,
class initialization, final fields) answers "how does a reader see a
constructed object?" Finals answer the narrowest version: "at least the
`final` state is visible, no matter how the reference travelled."

## Designing immutable value types

An immutable class is a freeze beneficiary by construction:

- All state in `final` fields, assigned once in the constructor.
- No `this` exposure during construction (no listener registration, no
  thread start, no static install, no overridable-method call).
- Mutable inputs defensively copied into `final` storage (arrays, lists)
  so the transitive rule covers something actually immutable.

Such a class needs no synchronization for reads after publication, under
any publication path, including races. That is why `String`, records,
and `List.of` collections are calm under sharing: the architecture is
"snapshot at construction, freeze, then share freely."

## Layering finals with other mechanisms

| Layer | Responsibility |
|---|---|
| `final` + no escape | Initialization visibility (once, zero read cost) |
| `volatile` reference | Later mutation visibility |
| Lock | Compound invariants and check-then-act |
| Holder / enum | Lazy or eager one-time installation |

Use finals for the construction layer and add exactly one mechanism per
further need. A `final ArrayList` field is safely published as a pointer;
its later `add` calls still need their own synchronization.

## Constructor discipline as an architectural rule

Treat constructors as two phases: store first, publish last (or never).
Any framework hook that runs inside construction (listener callbacks,
subclass overrides of called methods, DI post-processors that expose
the bean early) must come after all final stores, or the freeze protects
nothing. Review constructors for publication statements the way you
review lock scopes.

## Deserialization-shaped paths

Allocate-then-fill paths (`readObject`, `Unsafe.allocateInstance` plus
field fills) skip the constructor freeze. Frameworks that use them must
supply their own ordering (fences or volatile publication); custom
`readObject` code must reason about publication explicitly instead of
assuming final-like safety.

## Takeaway

Architecture with finals means: immutable snapshots for shared state,
strict store-before-publish constructors, and explicit mechanisms for
anything mutated after construction. The freeze is free and total for
initialization; it promises nothing beyond it.
