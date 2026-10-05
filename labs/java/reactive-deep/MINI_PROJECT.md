# Mini Project — Reactive Java Deep Dive (reactive-deep)

Build in 2–4h: small app exercising Reactor, RxJava, Flow API, backpressure.

## Goal
A CLI/demo app that uses at least 4 of: Publisher/Subscriber, Flux/Mono, backpressure strategies, schedulers.

## Requirements
- [ ] Use `Publisher/Subscriber` with a visible behavior/test.
- [ ] Use `Flux/Mono` with a visible behavior/test.
- [ ] Use `backpressure strategies` with a visible behavior/test.
- [ ] Use `schedulers` with a visible behavior/test.
- [ ] Use `error handling` with a visible behavior/test.
- [ ] Use `testing with StepVerifier` with a visible behavior/test.
- [ ] 3+ JUnit tests green.
- [ ] README with run + sample output.

## Steps
1. Scaffold Maven module.
2. Implement core loop.
3. Add tests + one metric (time/heap/threads).
4. Demo script (5 min).

## Starter sketch
```java
// reactive-deep mini: combine Publisher/Subscriber + Flux/Mono
public class MiniApp {
  public static void main(String[] a) { System.out.println("mini running"); }
}
```

## Rubric (10)
- Functionality 4, tests 2, clarity 2, metric 2.
Stretch 0: add Publisher/Subscriber variant.
Stretch 1: add Flux/Mono variant.
Stretch 2: add backpressure strategies variant.
Stretch 3: add schedulers variant.
Stretch 4: add error handling variant.
Stretch 5: add testing with StepVerifier variant.
Stretch 6: add R2DBC/reactive web variant.
Stretch 7: add virtual threads vs reactive variant.
Stretch 8: add Publisher/Subscriber variant.
Stretch 9: add Flux/Mono variant.
Stretch 10: add backpressure strategies variant.
Stretch 11: add schedulers variant.
Stretch 12: add error handling variant.
Stretch 13: add testing with StepVerifier variant.
Stretch 14: add R2DBC/reactive web variant.
Stretch 15: add virtual threads vs reactive variant.
Stretch 16: add Publisher/Subscriber variant.
Stretch 17: add Flux/Mono variant.
Stretch 18: add backpressure strategies variant.
Stretch 19: add schedulers variant.
Stretch 20: add error handling variant.
Stretch 21: add testing with StepVerifier variant.
Stretch 22: add R2DBC/reactive web variant.
Stretch 23: add virtual threads vs reactive variant.
Stretch 24: add Publisher/Subscriber variant.
Stretch 25: add Flux/Mono variant.
Stretch 26: add backpressure strategies variant.
Stretch 27: add schedulers variant.
Stretch 28: add error handling variant.
Stretch 29: add testing with StepVerifier variant.
Stretch 30: add R2DBC/reactive web variant.
Stretch 31: add virtual threads vs reactive variant.
Stretch 32: add Publisher/Subscriber variant.
Stretch 33: add Flux/Mono variant.
Stretch 34: add backpressure strategies variant.
Stretch 35: add schedulers variant.
Stretch 36: add error handling variant.
Stretch 37: add testing with StepVerifier variant.
Stretch 38: add R2DBC/reactive web variant.
Stretch 39: add virtual threads vs reactive variant.
Stretch 40: add Publisher/Subscriber variant.
Stretch 41: add Flux/Mono variant.
Stretch 42: add backpressure strategies variant.
Stretch 43: add schedulers variant.
Stretch 44: add error handling variant.
Stretch 45: add testing with StepVerifier variant.
Stretch 46: add R2DBC/reactive web variant.
Stretch 47: add virtual threads vs reactive variant.
Stretch 48: add Publisher/Subscriber variant.
Stretch 49: add Flux/Mono variant.
Stretch 50: add backpressure strategies variant.
Stretch 51: add schedulers variant.
Stretch 52: add error handling variant.
Stretch 53: add testing with StepVerifier variant.
Stretch 54: add R2DBC/reactive web variant.
Stretch 55: add virtual threads vs reactive variant.
Stretch 56: add Publisher/Subscriber variant.
