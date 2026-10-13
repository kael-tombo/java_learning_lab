# How It Works: Final Field Semantics

## Step 1: the constructor stores finals

```java
Holder(int a, String s) {
    this.a = a;
    this.s = s;
    this.arr = new int[]{a, a + 1};
}
```

Each store is a final write `w`. Program order inside the constructor
chains every `w` to the constructor end. Nothing is visible yet; this is
pure thread-local sequencing.

## Step 2: the constructor ends — the freeze

At constructor end the freeze `f` runs. Conceptually it stamps all
preceding final writes: any thread that later reads these finals
*through this object's reference* is ordered after the stamp. The
compiler implements the stamp by forbidding reorderings of the final
stores past constructor end (plus platform stores where needed); the
reader side needs no fence because the dereference chain carries the
ordering.

## Step 3: publication, however sloppy

`shared = new Holder(...)` into a plain static races with readers. Under
ordinary field rules that race would doom visibility. Under 17.5 the
publication action `a` links into the freeze chain instead of standing
alone: `f ->hb a` is the bridge from construction to the wild.

## Step 4: the reader loads the reference

A reader spins until `shared` is non-null. That load is `r1`, linked by
the memory chain: `a ->mc r1`. The chain holds even though `a ->r1`
crossed a data race — this is the link ordinary happens-before cannot
supply and the freeze rule adds.

## Step 5: the reader dereferences into finals

`h.a`, `h.s`, `h.arr[0]` are `r2` reads, linked by the dereference
chain `r1 ->dc r2`. The full chain `w ->hb f ->hb a ->mc r1 ->dc r2`
fires, and the reader observes the constructed values — 3000 rounds out
of 3000, on every compliant JVM.

## Step 6 (failure mode): escape before the freeze

If the constructor publishes `this` first and stores second, the early
reader's `r1` precedes `f`. The chain cannot form (no freeze stands
between `w` and `a`), and the default-0 read is legal. The lab's 300 ms
sleep makes this ordering certain rather than racy.

## Step 7 (boundary): mutation after the freeze

Stores after construction have no freeze behind them. A later `arr[0] =`
or `list.add` travels under ordinary race rules and needs its own
`volatile`, lock, or immutability. The freeze is a one-time stamp, not a
standing shield.
