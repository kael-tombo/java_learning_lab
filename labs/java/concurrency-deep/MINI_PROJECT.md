# Mini Project — Concurrency Deep & Virtual Threads (concurrency-deep)

Build in 2–4h: small app exercising JMM, Loom, structured concurrency, VarHandles.

## Goal
A CLI/demo app that uses at least 4 of: JMM happens-before, virtual threads & carriers, structured concurrency, scoped values.

## Requirements
- [ ] Use `JMM happens-before` with a visible behavior/test.
- [ ] Use `virtual threads & carriers` with a visible behavior/test.
- [ ] Use `structured concurrency` with a visible behavior/test.
- [ ] Use `scoped values` with a visible behavior/test.
- [ ] Use `ForkJoinPool` with a visible behavior/test.
- [ ] Use `StampedLock/LongAdder` with a visible behavior/test.
- [ ] 3+ JUnit tests green.
- [ ] README with run + sample output.

## Steps
1. Scaffold Maven module.
2. Implement core loop.
3. Add tests + one metric (time/heap/threads).
4. Demo script (5 min).

## Starter sketch
```java
// concurrency-deep mini: combine JMM happens-before + virtual threads & carriers
public class MiniApp {
  public static void main(String[] a) { System.out.println("mini running"); }
}
```

## Rubric (10)
- Functionality 4, tests 2, clarity 2, metric 2.
Stretch 0: add JMM happens-before variant.
Stretch 1: add virtual threads & carriers variant.
Stretch 2: add structured concurrency variant.
Stretch 3: add scoped values variant.
Stretch 4: add ForkJoinPool variant.
Stretch 5: add StampedLock/LongAdder variant.
Stretch 6: add VarHandle variant.
Stretch 7: add reactive vs virtual variant.
Stretch 8: add JMM happens-before variant.
Stretch 9: add virtual threads & carriers variant.
Stretch 10: add structured concurrency variant.
Stretch 11: add scoped values variant.
Stretch 12: add ForkJoinPool variant.
Stretch 13: add StampedLock/LongAdder variant.
Stretch 14: add VarHandle variant.
Stretch 15: add reactive vs virtual variant.
Stretch 16: add JMM happens-before variant.
Stretch 17: add virtual threads & carriers variant.
Stretch 18: add structured concurrency variant.
Stretch 19: add scoped values variant.
Stretch 20: add ForkJoinPool variant.
Stretch 21: add StampedLock/LongAdder variant.
Stretch 22: add VarHandle variant.
Stretch 23: add reactive vs virtual variant.
Stretch 24: add JMM happens-before variant.
Stretch 25: add virtual threads & carriers variant.
Stretch 26: add structured concurrency variant.
Stretch 27: add scoped values variant.
Stretch 28: add ForkJoinPool variant.
Stretch 29: add StampedLock/LongAdder variant.
Stretch 30: add VarHandle variant.
Stretch 31: add reactive vs virtual variant.
Stretch 32: add JMM happens-before variant.
Stretch 33: add virtual threads & carriers variant.
Stretch 34: add structured concurrency variant.
Stretch 35: add scoped values variant.
Stretch 36: add ForkJoinPool variant.
Stretch 37: add StampedLock/LongAdder variant.
Stretch 38: add VarHandle variant.
Stretch 39: add reactive vs virtual variant.
Stretch 40: add JMM happens-before variant.
Stretch 41: add virtual threads & carriers variant.
Stretch 42: add structured concurrency variant.
Stretch 43: add scoped values variant.
Stretch 44: add ForkJoinPool variant.
Stretch 45: add StampedLock/LongAdder variant.
Stretch 46: add VarHandle variant.
Stretch 47: add reactive vs virtual variant.
Stretch 48: add JMM happens-before variant.
Stretch 49: add virtual threads & carriers variant.
Stretch 50: add structured concurrency variant.
Stretch 51: add scoped values variant.
Stretch 52: add ForkJoinPool variant.
Stretch 53: add StampedLock/LongAdder variant.
Stretch 54: add VarHandle variant.
Stretch 55: add reactive vs virtual variant.
Stretch 56: add JMM happens-before variant.
