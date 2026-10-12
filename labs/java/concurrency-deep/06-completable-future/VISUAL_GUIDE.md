# Visual Guide: CompletableFuture Pipelines

## Thread-placement map

```text
main: completedFuture("x").thenApply(f)        -> f runs in main (no pool)
worker W (supplyAsync body ends -> complete)   -> sync dependents run in W
commonPool-worker (thenApplyAsync, no exec)    -> async default
ioPool thread (thenApplyAsync(f, ioPool))      -> named executor
```

Draw every stage arrow labeled with its thread. Unlabeled arrows are the
placement bug.

## Map vs flatMap shapes

```text
thenApply (map):     CF<User> --User->String--> CF<String>
thenCompose (flat):  CF<User> --User->CF<Orders>--> CF<Orders>   (one box opened)
BROKEN thenApply:    CF<User> --User->CF<Orders>--> CF<CF<Orders>> (box in a box)
```

The nested-box drawing is the diagnostic: two borders = wrong combinator.

## allOf barrier

```text
a =======>+
b =======>+---> [allOf: CF<Void>, value null] ---> thenApply(v -> (a.join(), b.join()))
c =======>+
```

The barrier node holds no values (draw it empty). Value arrows come from the
inputs, never through the barrier. Failure arrow carries the first exception;
siblings drawn as suppressed side-arrows.

## anyOf race

```text
primary ....---> [anyOf: CF<Object>] ---> cast ---> use
replica ..--->X (loser: STILL RUNNING until cancel(false))
```

Draw the loser with a live arrow past the finish — `anyOf` never cuts it.
The cancel `X` must be drawn by hand.

## Handler flow

```text
failing CF ---> exceptionally(f) ---> recovered value (or new failure if f throws)
failing CF ---> handle((v,ex))  ---> unified value, both paths land here
failing CF ---> whenComplete    ---> same failure out (observation tap, no change)
```

`whenComplete` drawn as a side-tap, not a transformer — its return wire goes
nowhere.

## Cancel race diagram

```text
result: null --complete(v)--> V      (late cancel returns false)
result: null --cancel()----> Cancelled (late complete returns false, body still runs)
```

Two arrows into one slot; only the first lands. The body's execution bar is
drawn separately — cancel never shortens it.
