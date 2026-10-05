# Mini Project — Java Performance Engineering (performance-deep)

Build in 2–4h: small app exercising JMH, JIT, profiling, GC latency.

## Goal
A CLI/demo app that uses at least 4 of: JMH benchmarks, JIT C1/C2 & inlining, escape analysis, allocation profiling.

## Requirements
- [ ] Use `JMH benchmarks` with a visible behavior/test.
- [ ] Use `JIT C1/C2 & inlining` with a visible behavior/test.
- [ ] Use `escape analysis` with a visible behavior/test.
- [ ] Use `allocation profiling` with a visible behavior/test.
- [ ] Use `async-profiler/JFR` with a visible behavior/test.
- [ ] Use `GC pause tuning` with a visible behavior/test.
- [ ] 3+ JUnit tests green.
- [ ] README with run + sample output.

## Steps
1. Scaffold Maven module.
2. Implement core loop.
3. Add tests + one metric (time/heap/threads).
4. Demo script (5 min).

## Starter sketch
```java
// performance-deep mini: combine JMH benchmarks + JIT C1/C2 & inlining
public class MiniApp {
  public static void main(String[] a) { System.out.println("mini running"); }
}
```

## Rubric (10)
- Functionality 4, tests 2, clarity 2, metric 2.
Stretch 0: add JMH benchmarks variant.
Stretch 1: add JIT C1/C2 & inlining variant.
Stretch 2: add escape analysis variant.
Stretch 3: add allocation profiling variant.
Stretch 4: add async-profiler/JFR variant.
Stretch 5: add GC pause tuning variant.
Stretch 6: add lock contention variant.
Stretch 7: add vector API variant.
Stretch 8: add JMH benchmarks variant.
Stretch 9: add JIT C1/C2 & inlining variant.
Stretch 10: add escape analysis variant.
Stretch 11: add allocation profiling variant.
Stretch 12: add async-profiler/JFR variant.
Stretch 13: add GC pause tuning variant.
Stretch 14: add lock contention variant.
Stretch 15: add vector API variant.
Stretch 16: add JMH benchmarks variant.
Stretch 17: add JIT C1/C2 & inlining variant.
Stretch 18: add escape analysis variant.
Stretch 19: add allocation profiling variant.
Stretch 20: add async-profiler/JFR variant.
Stretch 21: add GC pause tuning variant.
Stretch 22: add lock contention variant.
Stretch 23: add vector API variant.
Stretch 24: add JMH benchmarks variant.
Stretch 25: add JIT C1/C2 & inlining variant.
Stretch 26: add escape analysis variant.
Stretch 27: add allocation profiling variant.
Stretch 28: add async-profiler/JFR variant.
Stretch 29: add GC pause tuning variant.
Stretch 30: add lock contention variant.
Stretch 31: add vector API variant.
Stretch 32: add JMH benchmarks variant.
Stretch 33: add JIT C1/C2 & inlining variant.
Stretch 34: add escape analysis variant.
Stretch 35: add allocation profiling variant.
Stretch 36: add async-profiler/JFR variant.
Stretch 37: add GC pause tuning variant.
Stretch 38: add lock contention variant.
Stretch 39: add vector API variant.
Stretch 40: add JMH benchmarks variant.
Stretch 41: add JIT C1/C2 & inlining variant.
Stretch 42: add escape analysis variant.
Stretch 43: add allocation profiling variant.
Stretch 44: add async-profiler/JFR variant.
Stretch 45: add GC pause tuning variant.
Stretch 46: add lock contention variant.
Stretch 47: add vector API variant.
Stretch 48: add JMH benchmarks variant.
Stretch 49: add JIT C1/C2 & inlining variant.
Stretch 50: add escape analysis variant.
Stretch 51: add allocation profiling variant.
Stretch 52: add async-profiler/JFR variant.
Stretch 53: add GC pause tuning variant.
Stretch 54: add lock contention variant.
Stretch 55: add vector API variant.
Stretch 56: add JMH benchmarks variant.
