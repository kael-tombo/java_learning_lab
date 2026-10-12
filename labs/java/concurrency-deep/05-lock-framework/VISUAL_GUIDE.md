# Visual Guide: AQS Queue

## The steady state

```text
head(dummy, served) <-> B(thread, WAITING) <-> C(thread, parked)
tail -> C
state = 1 (held by A)
```

A holds the lock (`state = 1`). B and C queued in arrival order. B's
predecessor is head, so B retries first on every wakeup; C stays parked until
B becomes head and unparks it.

## Acquire race (barging)

```text
unlock: state 1 -> 0, unpark B
  ... gap ...
D (newcomer): CAS(0 -> 1) SUCCEEDS -> owns lock
B (woken):    tryAcquire FAILS (state = 1 again) -> re-parks
```

The gap between `unlock`'s unpark and B's retry is the barging window. Fair
mode closes the *overt* version (D checks the queue first); the gap race
itself never fully closes.

## Cancellation healing

```text
before: head <-> B(CANCELLED) <-> C
after:  head <-------------> C   (C.prev reset to head)
```

B's interrupt marks it `CANCELLED`; C's next retry walks back past B to head.
No other node moves — a local repair, not a rebuild.

## Condition migration

```text
sync queue:              head <-> B
condition queue (notEmpty): W1 -> W2

signal() moves W1:
sync queue:              head <-> B <-> W1 (tail)
condition queue (notEmpty): W2
```

W1 must still win a `tryAcquire` race from the tail — drawn after B and any
bargers. Ownership is never drawn as an arrow from `signal`; only queue
membership moves.

## RWLock packed state

```text
state (32 bits): [ reader count: high 16 | writer holds: low 16 ]
example: readers=2, writer=1 -> 0x00020001
```

One CAS updates either half. Reader 65536 would spill into the writer half —
hence the overflow throw instead of silent corruption.

## Semaphore permits

```text
permits=5: [o][o][o][o][o]  acquire(2) -> [o][o][o] + 2 held
release() without acquire -> [o][o][o][o][o][o]  (6! uncapped)
```

Draw every release matched to an acquire arrow; unmatched releases are the
drift bug made visible.
