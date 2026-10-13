# History: Final Field Semantics

## The problem: unsafe publication in the original memory model

Before Java 5, the memory model gave immutable objects no special
protection. Publishing a fully constructed object through a race could
expose default (zero/null) values for its fields to another thread, and
standard immutable classes relied on luck, documentation warnings, or
synchronized publication everywhere.

## JSR-133 and Java 5 (2004)

JSR-133 revised the Java Memory Model for Java 5. Its headline items
were the redefined `volatile` semantics and the new final-field
guarantee that became JLS 17.5: the constructor-end freeze with
memory-chain and dereference-chain ordering. From Java 5 on, correctly
constructed objects with final fields were safe under races as a matter
of specification, on every compliant JVM.

## JLS 17.5: the freeze rule

JLS 17.5 states the guarantee precisely: a final write ordered before
the freeze, chained through publication (`a`), a reference read (`r1`),
and a dereference (`r2`), is observed by the reader. The `this`-escape
exclusion is part of the same section: publication inside the
constructor precedes the freeze and gets no protection.

## Effective Java and immutable design

Joshua Bloch's *Effective Java* made immutability a mainstream design
prescription (immutable classes, final fields, defensive copies). The
17.5 guarantee is the memory-model foundation under that advice: Bloch's
immutable snapshot is exactly the object the freeze protects, provided
constructors store first and publish last.

## Records and immutable collections

Records (final components by construction) and `List.of`/`Map.of`
immutable collections extend the same guarantee into modern syntax: a
published record or immutable collection is a safely published snapshot
under races. The mutable-contents caveat is unchanged: finality of the
reference never confers immutability on a mutable referent.

## What did not change

The scope boundary has been stable since 2004: initialization only, no
`this` escape, no reflective or `Unsafe` post-construction writes. Later
editions of the JLS restate the rule without expanding it.
