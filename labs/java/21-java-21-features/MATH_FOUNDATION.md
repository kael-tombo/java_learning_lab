# Mathematical Foundations of Java 21 Features

## Virtual Threads: M:N Model

Virtual threads implement an **M:N threading model** where M virtual threads are scheduled onto N platform threads. The mathematics of this model derive from queueing theory and scheduling algorithms.

### Work-Conserving Scheduling
The virtual thread scheduler is **work-conserving**: a carrier thread is never idle if there is a runnable virtual thread. This is formalized as:

Let `V` = set of virtual threads, `C` = set of carrier threads (size N)
Let `state(v)` ∈ {RUNNABLE, BLOCKED, PARKED} for each v ∈ V

A work-conserving scheduler ensures:
```
∀t, |{c ∈ C : idle(c, t)}| = 0 ⇒ |{v ∈ V : runnable(v, t)}| = 0
```

where `idle(c, t)` is true if carrier `c` is idle at time `t`, and `runnable(v, t)` is true if virtual thread `v` is runnable.

### Scalability Formula
The expected throughput `T` of a virtual-thread-based server is:
```
T = min(V_max, C_eff / (1 - p_block))
```
where:
- `V_max` = maximum concurrent virtual threads (limited by heap size, ~200 bytes each)
- `C_eff` = effective carrier thread cycles per second (≈ cores × frequency × IPC)
- `p_block` = fraction of time a typical request spends blocked on I/O

For a typical web service where `p_block ≈ 0.9` (90% of time waiting for databases, caches, etc.), the denominator `(1 - 0.9) = 0.1`, giving a 10× increase in effective capacity over platform threads.

## Pattern Matching: Algebraic Data Types and Exhaustiveness

Pattern matching's mathematical foundation lies in **algebraic data types** (ADTs). Records correspond to **product types** (a Point is an x AND a y), while sealed classes correspond to **sum types** (a Shape is a Circle OR a Rectangle OR a Triangle).

### Product Types and Record Patterns
A record `Point(int x, int y)` represents a product type `P = X × Y`. The number of possible values is `|P| = |X| × |Y|`. Record patterns deconstruct the product into its components.

### Sum Types and Exhaustiveness
A sealed interface `Shape` with `Circle`, `Rectangle`, and `Triangle` represents a sum type `S = C + R + T`. The number of possible values is `|S| = |C| + |R| + |T|`.

Exhaustiveness checking verifies that a switch over `Shape` has a branch for each variant. The compiler computes:
```
covered(S) = {C} ∪ {R} ∪ {T} ∪ {default}
```

The switch is exhaustive if `permits(S) ⊆ covered(S)`.

### Dominance
A pattern `p` dominates pattern `q` if `match_set(p) ⊇ match_set(q)` — every value matched by `q` is also matched by `p`. For example, `Object o` dominates `String s` because all strings are objects but not vice versa.

## Sequenced Collections: Order Theory

Sequenced collections are grounded in **order theory**. A collection `C` with sequence `≤_C` has:

1. **Total order**: For any a, b in `C`, either `a ≤_C b` or `b ≤_C a`
2. **First element**: `∃f ∈ C : ∀x ∈ C, f ≤_C x`
3. **Last element**: `∃l ∈ C : ∀x ∈ C, x ≤_C l`
4. **Reverse order**: `≤_C_rev` where `a ≤_C_rev b` iff `b ≤_C a`

The `reversed()` view implements `≤_C_rev` without copying, using a bijection between positions.

## String Templates: Template Processing

> **Status**: String Templates were previewed in JDK 21/22 and withdrawn before JDK 23; the formal model below describes the withdrawn feature and its `String.formatted` analogue.

String templates specified a form of **string interpolation with context-free processing**. Formally, a template `T` with fragments `f₁...fₙ₊₁` and expressions `e₁...eₙ` is:

```
T = f₁ ~ e₁ ~ f₂ ~ e₂ ~ ... ~ fₙ ~ eₙ ~ fₙ₊₁
```

where `~` denotes concatenation. A processor `P` transforms this into:
```
P(T) = process(f₁, e₁, f₂, e₂, ..., fₙ, eₙ, fₙ₊₁)
```

For `STR`, `process` is identity on fragments and `toString()` on values — the same shape as `"Hello %s".formatted(name)`, where the format string plays the fragments:
```
STR(T) = f₁ + toString(e₁) + f₂ + toString(e₂) + ... + fₙ + toString(eₙ) + fₙ₊₁
```

## Structured Concurrency: Task Dependency Graphs

Structured concurrency implements a **tree-structured task model** that enforces the **structured programming principle**:

A computation `C` has subcomputations `c₁, c₂, ..., cₙ`. The structured concurrency constraint requires:

```
lifetime(cᵢ) ⊆ lifetime(C)   for all i ∈ {1, ..., n}
termination(C) ⇒ termination(cᵢ)   for all i
exception(cᵢ) ⇒ cancellation(cⱼ)   for all j ≠ i (in ShutdownOnFailure mode)
```

This creates a partial order where child tasks cannot outlive their parent scope. The mathematical advantage is **deterministic resource management** — the number of active tasks at any time is bounded by the depth and branching factor of the task tree, not by the total duration of the program.
