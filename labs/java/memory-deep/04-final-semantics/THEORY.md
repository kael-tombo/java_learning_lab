# Final Field Semantics — Theoretical Foundation

## Core Concept

JLS §17.5 gives `final` fields a guarantee no other plain field has:
**initialization safety**. If an object is constructed without leaking
`this`, then *every* thread that ever sees its reference — through a race,
through a data race, through any publication path at all — observes its
`final` fields fully initialized. No `volatile`, no lock, no happens-before
edge on the reference itself. The constructor's end acts as a *freeze*:
stores to finals before it are ordered before any read of them after it,
full stop.

## The Freeze Rule (JLS §17.5, precisely)

For a final field write `w`, the freeze `f` (end of constructor), a
publication action `a`, a reference read `r1`, and a final-field read `r2`:

```
w →hb f →hb a →mc r1 →dc r2   ⟹   r2 observes w (or a later write)
```

- `→hb` is ordinary happens-before (program order inside the constructor
  chains `w` to `f`).
- `→mc` (memory chain) and `→dc` (dereference chain) extend ordering
  *through* the reference: if you obtain the reference somehow (`r1`), and
  read its final through it (`r2`), the freeze protects you — even when
  `a→r1` crossed a data race.
- The rule covers *transitives*: finals reachable through finals of
  safely-published objects inherit the protection (an immutable graph is
  safe as a whole — `String`'s `value` array elements included).

What it does **not** cover: mutable fields of the same object (ordinary
race rules apply), `final` fields of objects whose `this` escaped during
construction (no freeze precedes the escape), and writes to finals via
reflection/`Unsafe` after construction (freeze already passed —
`Field.setAccessible` mutation of finals is outside the model; results are
unspecified and version-dependent).

## The `this`-Escape Hazard

```java
class Leaky {
    static Leaky published;
    final int x;
    Leaky() {
        published = this;   // escape BEFORE x is stored: no freeze yet
        x = 42;             // too late — a reader may already hold the ref
    }
}
```

A reader that loads `published` between the escape and the store observes
`x == 0` — legally. The freeze happens at constructor *end*; publication
*inside* the constructor precedes it. This covers: registering listeners /
starting threads / publishing to statics from constructors, inner-class
references to outer `this` leaking early, and deserialization frameworks
that allocate-then-fill (they must use their own fences — which is why
`readObject`/`Unsafe.allocateInstance` paths have explicit safety
protocols, not JLS coverage).

Rule for constructors: touch nothing shared until fields are stored —
publish (register, start, expose) strictly last, or never.

## Why String (and Records, and List.of) Are Free Thread Safety

- `String`: `final byte[] value` + `final byte coder` — every `String`
  ever shared across threads without synchronization is safe *by §17.5*,
  including the array *contents* (transitive rule). String's thread safety
  is a theorem about finals, not about locks (there are none on the read
  path).
- Records: all components final — a published record is a published
  snapshot, safe under races by construction.
- `List.of`/`Map.of` immutable collections: final-field-backed snapshots
  with the same guarantee (their iterators never `ConcurrentModification`
  because there is nothing to modify — a different mechanism, same
  observable calm).

## Finals vs Volatile vs Locks (when each carries publication)

| Mechanism | Covers | Cost |
|---|---|---|
| `final` + no escape | initialization (once) | zero (freeze is compile-time ordering) |
| `volatile` reference | all subsequent mutations too | fence per access |
| lock | compound invariants + mutations | monitor ops |
| `static` holder / enum | lazy init, once | class-init lock (one-time) |

Finals cover *construction*; everything after needs another mechanism. A
`final ArrayList` field is safely *published* but its *contents* mutate
under ordinary race rules — finality of the reference never extends to
mutability of the referent (the most quoted final-misunderstanding, stated
plainly).

## Key Invariants

1. Freeze at constructor end orders final stores before any post-construction
   final read, through any publication path (mc/dc chains).
2. `this` must not escape before field stores — escape voids the guarantee
   for early readers.
3. Transitivity: finals-of-finals of safely-published objects are safe
   (immutable graphs, not just fields).
4. Finals cover initialization only; later mutation needs volatile/locks.
5. Reflective/`Unsafe` post-construction writes to finals are outside the
   model — unspecified behavior, do not rely on any observed outcome.
