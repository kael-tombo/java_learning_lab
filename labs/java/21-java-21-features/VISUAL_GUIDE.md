# Visual Guide to Java 21 Features

## Virtual Threads Lifecycle

```
                    ┌─────────────┐
                    │  CREATED    │
                    │ (unstarted) │
                    └──────┬──────┘
                           │ start()
                           ▼
                    ┌─────────────┐
        ┌───────────│  RUNNABLE   │◄────────── unpark()
        │           │ (mounted on │
        │           │  carrier)   │
        │           └──────┬──────┘
        │                  │ park() / blocking I/O
        │                  ▼
        │           ┌─────────────┐
        │           │   PARKED    │
        │           │ (unmounted, │
        │           │  on heap)   │
        │           └──────┬──────┘
        │                  │ I/O completes / unpark()
        └──────────────────┘
```

## Carrier Thread Scheduling

```
Time ──────────────────────────────────────────────►

Carrier-1: | VT-A | VT-B |      | VT-A | VT-D |      |
Carrier-2: | VT-C |      | VT-D | VT-B |      | VT-E |
Carrier-3: |      | VT-A | VT-C |      | VT-E | VT-B |
           └──────┴──────┴──────┴──────┴──────┴──────┘

VT-A: Runnable→Pinned→Runnable→Parked→Runnable
VT-B: Runnable→Parked→Runnable
VT-C: Runnable→Parked
VT-D: Runnable→Runnable→Parked
VT-E: Runnable→Runnable
```

## Pattern Matching Structure

```
switch (shape) {
    ┌─ case Circle(double r) ──────────────┐
    │  Pattern: type match + record decon   │
    │  Guard: optional (r > 0)              │
    │  Body: process circle                 │
    └───────────────────────────────────────┘
    ┌─ case Rectangle(double w, double h) ──┐
    │  Pattern: type match + record decon   │
    │  Guard: when w > 0 && h > 0           │
    │  Body: process rectangle              │
    └───────────────────────────────────────┘
    ┌─ default ─────────────────────────────┐
    │  Catch-all for uncovered cases        │
    └───────────────────────────────────────┘
}
```

## Sequenced Collection Operations

```
Forward order (insertion order):
  [A] → [B] → [C] → [D] → [E]
   ↑                          ↑
   getFirst()               getLast()
   addFirst(X)              addLast(Z)
   removeFirst()            removeLast()

Reversed view:
  [E] → [D] → [C] → [B] → [A]
```

## Sequenced Collection Hierarchy

```
                  Iterable
                      │
                 Collection
                  ╱       ╲
       SequencedCollection  Queue
          ╱     ╲         ╱
SequencedSet    List    Deque
    ╱
NavigableSet

SequencedMap (separate parallel hierarchy)
```

## String Template Processing

String Templates were previewed in JDK 21/22 and withdrawn before JDK 23 — the pipeline below is historical, shown to explain the fragments/values model that this lab still teaches:

```
Template: "Hello \{name}, age \{age}"   (withdrawn preview syntax)

Fragments: ["Hello ", ", age ", ""]
Values:    [name, age]

Processor (STR):
  "Hello " + name + ", age " + age
  → "Hello João, age 30"

Processor (FMT):
  "Hello %s%s, age %d" format with name, "", age
  → "Hello João, age 30"

Custom SQL Processor:
  → PreparedStatement with ? parameters

Compiling today, the same output comes from:
  "Hello %s, age %d".formatted(name, age)
```

## Structured Concurrency Scope

```
┌─ try (var scope = new StructuredTaskScope.ShutdownOnFailure()) ──┐
│                                                                    │
│  │ fork(findUser())─────►│  │ fork(findAddress())─────►│         │
│  │   running. . . done   │  │   running. . . done      │         │
│                                                                    │
│  │ scope.join() ◄────────┘  ┘                                     │
│  │ scope.throwIfFailed()                                          │
│  │ return new Response(user.get(), addr.get())                    │
│                                                                    │
└── scope.close() (in finally, auto through try-with-resources) ───┘
```
