# Mini Project — Java Memory Management (memory-management)

Build in 2–4h: small app exercising allocation, GC tuning, leak detection, heap dumps.

## Goal
A CLI/demo app that uses at least 4 of: allocation paths (TLAB), young/old GC, G1/ZGC/Shenandoah, tuning flags.

## Requirements
- [ ] Use `allocation paths (TLAB)` with a visible behavior/test.
- [ ] Use `young/old GC` with a visible behavior/test.
- [ ] Use `G1/ZGC/Shenandoah` with a visible behavior/test.
- [ ] Use `tuning flags` with a visible behavior/test.
- [ ] Use `leak detection` with a visible behavior/test.
- [ ] Use `heap dump analysis` with a visible behavior/test.
- [ ] 3+ JUnit tests green.
- [ ] README with run + sample output.

## Steps
1. Scaffold Maven module.
2. Implement core loop.
3. Add tests + one metric (time/heap/threads).
4. Demo script (5 min).

## Starter sketch
```java
// memory-management mini: combine allocation paths (TLAB) + young/old GC
public class MiniApp {
  public static void main(String[] a) { System.out.println("mini running"); }
}
```

## Rubric (10)
- Functionality 4, tests 2, clarity 2, metric 2.
Stretch 0: add allocation paths (TLAB) variant.
Stretch 1: add young/old GC variant.
Stretch 2: add G1/ZGC/Shenandoah variant.
Stretch 3: add tuning flags variant.
Stretch 4: add leak detection variant.
Stretch 5: add heap dump analysis variant.
Stretch 6: add OOM causes variant.
Stretch 7: add direct memory variant.
Stretch 8: add allocation paths (TLAB) variant.
Stretch 9: add young/old GC variant.
Stretch 10: add G1/ZGC/Shenandoah variant.
Stretch 11: add tuning flags variant.
Stretch 12: add leak detection variant.
Stretch 13: add heap dump analysis variant.
Stretch 14: add OOM causes variant.
Stretch 15: add direct memory variant.
Stretch 16: add allocation paths (TLAB) variant.
Stretch 17: add young/old GC variant.
Stretch 18: add G1/ZGC/Shenandoah variant.
Stretch 19: add tuning flags variant.
Stretch 20: add leak detection variant.
Stretch 21: add heap dump analysis variant.
Stretch 22: add OOM causes variant.
Stretch 23: add direct memory variant.
Stretch 24: add allocation paths (TLAB) variant.
Stretch 25: add young/old GC variant.
Stretch 26: add G1/ZGC/Shenandoah variant.
Stretch 27: add tuning flags variant.
Stretch 28: add leak detection variant.
Stretch 29: add heap dump analysis variant.
Stretch 30: add OOM causes variant.
Stretch 31: add direct memory variant.
Stretch 32: add allocation paths (TLAB) variant.
Stretch 33: add young/old GC variant.
Stretch 34: add G1/ZGC/Shenandoah variant.
Stretch 35: add tuning flags variant.
Stretch 36: add leak detection variant.
Stretch 37: add heap dump analysis variant.
Stretch 38: add OOM causes variant.
Stretch 39: add direct memory variant.
Stretch 40: add allocation paths (TLAB) variant.
Stretch 41: add young/old GC variant.
Stretch 42: add G1/ZGC/Shenandoah variant.
Stretch 43: add tuning flags variant.
Stretch 44: add leak detection variant.
Stretch 45: add heap dump analysis variant.
Stretch 46: add OOM causes variant.
Stretch 47: add direct memory variant.
Stretch 48: add allocation paths (TLAB) variant.
Stretch 49: add young/old GC variant.
Stretch 50: add G1/ZGC/Shenandoah variant.
Stretch 51: add tuning flags variant.
Stretch 52: add leak detection variant.
Stretch 53: add heap dump analysis variant.
Stretch 54: add OOM causes variant.
Stretch 55: add direct memory variant.
Stretch 56: add allocation paths (TLAB) variant.
