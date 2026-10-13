# Exercises: Final Field Semantics

All snippets run on JDK 9+ with no dependencies. Keep `println` output
pure ASCII.

## 1. Freeze through a race (baseline)

Run `FinalViaRace` as given: 3000 rounds, plain racy static, assert
`a`, `s`, `arr[0]`, `arr[1]` exact every round. Confirm output:

```
rounds = 3000
all finals (incl. transitive array) exact, every round: true
```

Then raise to 10000 rounds and confirm it stays exact. This is the
guarantee; more rounds should not shake it.

## 2. Break the transitivity deliberately

Modify `Holder` to alias a caller-owned array instead of allocating:

```java
Holder(int a, String s, int[] ext) {
    this.a = a;
    this.s = s;
    this.arr = ext;  // no defensive copy
}
```

Mutate `ext[0]` after publication from the writer thread and observe
the reader seeing the mutation. Restore the defensive copy and confirm
exactness returns. Write down which version the freeze protects.

## 3. Wedge the escape window

Run `ThisEscape` as given and confirm the deterministic read:

```
observed during construction window = 0
default value observed (freeze not yet run): true
final value after construction = 42
```

Then move `published = this` to the last constructor line (after the
store and sleep) and show the early reader now blocks until 42 is
stored. No timing luck should remain in either direction.

## 4. Mutable twin comparison

Run `MutableControl` and confirm `stale rounds = 0/3000` on this
machine. Then write a short paragraph: why does this identical-looking
green run carry zero guarantee while exercise 1 carries a JLS guarantee?
Name the hardware property (TSO + coherence) doing the hiding.

## 5. Record with mutable contents

Build a record holding an `ArrayList`, publish it through the same racy
static, mutate the list after publication, and show the reader observing
the mutation. Swap the `ArrayList` for `List.of(...)` and show the
observation going exact. State the rule: finals publish the reference;
immutability of the referent is a separate requirement.

## 6. String handoff stress

Run `StringSharing` for 3000 rounds, then change the payload length
(short string vs 100-char repeat) and confirm intactness is independent
of length. Identify the two final fields (`value`, `coder`) responsible.

## 7. Reflection is outside the model (read-only)

Using a scratch program, reflectively set a final `int` after
construction and read it from a second thread. Record whatever you
observe, then delete the program: the point is that the outcome is
unspecified and version-dependent, so no assertion may rely on it.
