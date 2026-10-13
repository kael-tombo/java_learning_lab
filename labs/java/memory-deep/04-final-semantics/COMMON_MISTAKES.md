# Common Mistakes: Final Field Semantics

## 1. Publishing `this` from the constructor

```java
Leaky() {
    published = this;  // escape BEFORE the store
    x = 42;            // freeze comes too late
}
```

Any static install, listener registration, thread start, or callback
before the final stores lets a reader in through the pre-freeze window.
The lab demo wedges that window open 300 ms so the early read
deterministically sees default 0. Fix: store first, publish last.

## 2. Reading "final" as "immutable"

`final` on a reference publishes the pointer, not the referent. A
`final ArrayList` shared safely still races on `add`/`get`. The record
caveat in this lab is the same point: record components are safe, but a
record wrapping a mutable list leaves the list contents under ordinary
race rules. Only `List.of`-style genuinely immutable contents inherit
the transitive guarantee.

## 3. Trusting the mutable twin

The `MutableControl` snippet passes 3000 rounds on x86 and proves
nothing: TSO plus cache coherence hides the missing guarantee on this
hardware, on this JVM, today. A reordering JIT or weaker CPU may show
stale fields any day. Identical green runs, opposite meanings: snippet 1
is a theorem (JLS 17.5), snippet 4 is weather.

## 4. Calling overridable methods from constructors

An overridden method invoked from a superclass constructor observes the
subclass finals before they are stored (and can leak `this` to other
threads even earlier). Keep constructors private-or-final in behavior:
assign fields directly, call only private/static helpers.

## 5. Reflective post-construction writes to finals

`Field.setAccessible` mutation or `Unsafe` writes to a final after
construction sit outside the memory model. Observed behavior (other
threads seeing old, new, or mixed values; JIT constant-folding keeping
the old value forever) is version-dependent accident. Never use this as
a publication or update mechanism.

## 6. Assuming deserialization gets the freeze

Custom `readObject` or allocate-then-fill paths do not run the
constructor freeze. Assuming final-like safety there confuses the
constructor path with the framework path. Frameworks add their own
fences; hand-written `readObject` must handle publication explicitly.

## 7. Forgetting the transitive requirement

Finals-of-finals are safe only through a safely constructed chain. A
final array allocated and filled inside the constructor is covered; a
final array assigned from a caller-owned, still-mutated array is not.
Copy mutable inputs during construction.
