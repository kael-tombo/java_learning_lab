# Visual Guide: Scopes in Pictures

## Fan-out and rendezvous (ShutdownOnFailure)

```
owner ── fork A ──→ [thread A: fetchA] ──┐
      ── fork B ──→ [thread B: fetchB] ──┤
                                         ▼
                                   scope.join()   ← owner parks here
                                   throwIfFailed()
                                   A.get() + B.get()
      ─────────────────────────────────────────
      try block boundary = close() reaps stragglers
```

Handles A and B start `UNAVAILABLE`; after the rendezvous both read
`SUCCESS` and combine. One block, one wait, two answers.

## Fail-fast timeline

```
t0 ── fork slow ──→ sleeps ............ INTERRUPTED at t2
t0 ── fork bad ───→ throws at t1 ──→ policy shutdown() at t1
t1 ── join() returns early (no waiting for slow)
t2 ── close() reaps slow ──→ block exits, state: bad=FAILED
```

The failure at t1 decides the scope; the sibling's remaining sleep is
cancelled, not waited out.

## First-success race (ShutdownOnSuccess)

```
replica A ──→ FAILS at 30ms ──→ recorded, scope keeps waiting
replica B ──→ SUCCEEDS at 120ms ──→ shutdown(), result() = B
```

Failures before any success are tolerated, not propagated: the timeline
ends at the first success regardless of earlier failures.

## Deadline with joinUntil

```
fork slow (5s) ──→ runs .....
joinUntil(now+200ms) ──→ TimeoutException at 200ms
close() ──→ interrupts slow ──→ block exits ~200ms, nothing leaks
```

The owner's wait is bounded by the deadline while containment still
covers the full subtask lifetime.

## Ownership map

```
creates ──→ owner thread ── join/close/result ──→ OK
intruder thread ── join() ──→ WrongThreadException
subtask thread ── owns NESTED scope ──→ OK (its own scope only)
closed scope ── fork() ──→ IllegalStateException (any caller)
rebound values ── fork() ──→ StructureViolationException
```

## Nesting dolls

```
outer scope [ owner: main ]
 └─ subtask T ──→ inner scope [ owner: T's thread ]
     ├─ fork L ──→ leaf ──→ SUCCESS
     └─ fork R ──→ leaf ──→ SUCCESS
     inner join + throwIfFailed → T = L.get()+R.get() → SUCCESS
outer join + throwIfFailed → total
```

Inner `close()` seals grandchildren before the outer join observes T.

## State machine

```text
UNAVAILABLE ──returns──→ SUCCESS | ──throws──→ FAILED (terminal)
get() valid only on SUCCESS; exception() non-null only on FAILED.
```
