# Mini Project — JVM Memory Internals (memory-deep)

Build in 2–4h: small app exercising heap regions, metaspace, stack, GC internals, JOL, NMT.

## Goal
A CLI/demo app that uses at least 4 of: heap vs stack, eden/survivor/old gen, metaspace vs permgen, object header & alignment.

## Requirements
- [ ] Use `heap vs stack` with a visible behavior/test.
- [ ] Use `eden/survivor/old gen` with a visible behavior/test.
- [ ] Use `metaspace vs permgen` with a visible behavior/test.
- [ ] Use `object header & alignment` with a visible behavior/test.
- [ ] Use `GC roots & reachability` with a visible behavior/test.
- [ ] Use `NMT & JOL` with a visible behavior/test.
- [ ] 3+ JUnit tests green.
- [ ] README with run + sample output.

## Steps
1. Scaffold Maven module.
2. Implement core loop.
3. Add tests + one metric (time/heap/threads).
4. Demo script (5 min).

## Starter sketch
```java
// memory-deep mini: combine heap vs stack + eden/survivor/old gen
public class MiniApp {
  public static void main(String[] a) { System.out.println("mini running"); }
}
```

## Rubric (10)
- Functionality 4, tests 2, clarity 2, metric 2.
Stretch 0: add heap vs stack variant.
Stretch 1: add eden/survivor/old gen variant.
Stretch 2: add metaspace vs permgen variant.
Stretch 3: add object header & alignment variant.
Stretch 4: add GC roots & reachability variant.
Stretch 5: add NMT & JOL variant.
Stretch 6: add reference types variant.
Stretch 7: add safepoints variant.
Stretch 8: add heap vs stack variant.
Stretch 9: add eden/survivor/old gen variant.
Stretch 10: add metaspace vs permgen variant.
Stretch 11: add object header & alignment variant.
Stretch 12: add GC roots & reachability variant.
Stretch 13: add NMT & JOL variant.
Stretch 14: add reference types variant.
Stretch 15: add safepoints variant.
Stretch 16: add heap vs stack variant.
Stretch 17: add eden/survivor/old gen variant.
Stretch 18: add metaspace vs permgen variant.
Stretch 19: add object header & alignment variant.
Stretch 20: add GC roots & reachability variant.
Stretch 21: add NMT & JOL variant.
Stretch 22: add reference types variant.
Stretch 23: add safepoints variant.
Stretch 24: add heap vs stack variant.
Stretch 25: add eden/survivor/old gen variant.
Stretch 26: add metaspace vs permgen variant.
Stretch 27: add object header & alignment variant.
Stretch 28: add GC roots & reachability variant.
Stretch 29: add NMT & JOL variant.
Stretch 30: add reference types variant.
Stretch 31: add safepoints variant.
Stretch 32: add heap vs stack variant.
Stretch 33: add eden/survivor/old gen variant.
Stretch 34: add metaspace vs permgen variant.
Stretch 35: add object header & alignment variant.
Stretch 36: add GC roots & reachability variant.
Stretch 37: add NMT & JOL variant.
Stretch 38: add reference types variant.
Stretch 39: add safepoints variant.
Stretch 40: add heap vs stack variant.
Stretch 41: add eden/survivor/old gen variant.
Stretch 42: add metaspace vs permgen variant.
Stretch 43: add object header & alignment variant.
Stretch 44: add GC roots & reachability variant.
Stretch 45: add NMT & JOL variant.
Stretch 46: add reference types variant.
Stretch 47: add safepoints variant.
Stretch 48: add heap vs stack variant.
Stretch 49: add eden/survivor/old gen variant.
Stretch 50: add metaspace vs permgen variant.
Stretch 51: add object header & alignment variant.
Stretch 52: add GC roots & reachability variant.
Stretch 53: add NMT & JOL variant.
Stretch 54: add reference types variant.
Stretch 55: add safepoints variant.
Stretch 56: add heap vs stack variant.
