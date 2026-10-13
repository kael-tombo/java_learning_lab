# Visual Guide: DCL Pattern

## Correct volatile DCL (steady state + first race)

```
check (1): h = instance (volatile read)
   |-- non-null --> return h                    [fast path, every call]
   |-- null --+
              v
   synchronized (X.class) {       [slow path, null window only]
       check (2): (h = instance) == null ?
          |-- non-null --> return h             [lost the race, reuse]
          |-- null --> h = instance = new Helper();
                       |  allocate -> init (value=42, freeze)
                       |  volatile write publishes (release)
                       return h
   }
```

## Missing volatile (pre-2004 reorder)

```
T1 (writer)                        T2 (reader)
-----------                        -----------
allocate Helper
store ref FIRST (reordered!) -----> check (1): non-null
   ...                                read value ==> 0 (HALF-BUILT, legal pre-fix)
field stores (value=42) arrive too late
```

JSR-133's volatile write/read edge forbids exactly this shape — with
the keyword present.

## Missing recheck (deterministic double-init)

```
gate opens
T1: check(1) null ---+                    T2: check(1) null ---+
                     v                                         v
T1 enters monitor:   instance = new Helper()  [sleep 50 ms inside]
T1 exits (publishes #1)
T2 enters monitor:   NO recheck --> instance = new Helper()  (#2!)
Result: constructions = 2, first instance discarded, last write wins
```

With the recheck, T2's locked re-read observes #1 via the monitor edge
and skips construction.

## The alternatives at a glance

```
HOLDER:  get() -> LazyHolder.INSTANCE
                  ^-- JLS 12.4.2 class-init lock: once, lazy, JVM-owned

ENUM:    Directory.INSTANCE
                  ^-- eager; reflection throws; deserialize == identity

SYNC:    synchronized get(): monitor/call (~20 ns) -- obviously correct
DCL:     volatile read/call (~1 ns) -- subtle, needs all three elements
```

## Bloch local (one read, no skew)

```
GOOD:  h = instance (once) -> check h -> recheck into h -> return h
BAD:   check instance ... check instance ... return instance
       (two fences; returned object may differ from checked object)
```
