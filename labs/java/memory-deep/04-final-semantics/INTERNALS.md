# Internals: Final Field Semantics

## What the JIT and hardware must honor

JLS 17.5 binds the implementation, not just the programmer. The compiler
(JIT and `javac`-level ordering constraints) must not reorder final
stores past the constructor-end freeze, and must not reorder reads of
finals obtained through a reference ahead of the reference load in ways
that break the dereference chain. On strong hardware (x86 TSO) the
store side typically needs no explicit fence; on weaker architectures
the JVM inserts the required StoreStore barriers at the freeze.

## Why readers pay nothing

The dereference chain is carried by data dependence: loading the
reference and then the field through it. Because the consumer cannot
read the field before it holds the address, the CPU already orders the
two loads on every platform that matters, and the model blesses that
ordering as sufficient. Hence zero read-path cost — no volatile load,
no fence, no monitor — for final reads after any publication.

## Transitives in memory layout terms

`String`'s `value` array elements are covered because the array (final
reference, freshly allocated and filled inside construction) chains
through the same freeze: the element stores precede the array-reference
freeze, which precedes publication. HotSpot relies on this: `String`
sharing across threads performs no read-path synchronization at all.

## Constant folding interaction

The JIT may treat provably-unmodified finals as constants and fold them.
That is sound only because post-construction writes to finals are
outside the model: if you mutate a final reflectively, folded code may
keep returning the old value forever while other paths see the new one.
The observed split is not a JIT bug; the write was never in the model.

## Escape analysis is not the freeze

Do not confuse JIT escape analysis (stack allocation, lock elision) with
the 17.5 freeze. Escape analysis is an optimization the JIT may or may
not perform; the freeze is a specification guarantee the JVM must honor
for every construction, optimized or not.

## Implementation note

The freeze logic lives in the compilers (C1/C2 barrier emission,
`Parse::do_field_store` handling of final stores) and the interpreter's
field-store paths. Readers tracing the implementation should look at
final-store barrier code and the JMM-related comments there, not at any
user-level locking: there is deliberately none on the read side.
