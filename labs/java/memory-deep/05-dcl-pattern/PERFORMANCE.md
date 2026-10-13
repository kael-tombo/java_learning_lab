# Performance: DCL Pattern

## The two prices, framed structurally

- DCL fast path: one volatile read per `get()` (~1 ns framing, lab 03
  measurements). No monitor after warmup.
- Synchronized accessor: one monitor enter/exit pair per call (~20 ns
  uncontended). Same answers, different price.

DCL pays for itself only at high call rates (millions/second/thread);
below that, the synchronized accessor's obvious correctness wins. No
microbenchmark in this lab asserts the crossover — it moves with
hardware. Decide by structure (fence vs monitor), measure on the target
machine when it matters.

## The local-variable saving

Reading into `Helper h` once issues one acquire per call; reading the
field in both checks issues two. At DCL-worthy call rates the second
fence is real money for zero semantic gain — plus the skew hazard. The
Bloch shape is a (small) performance fix and a (large) correctness
clarification in one line.

## The recheck costs nothing on the fast path

Check (2) runs only inside the monitor, i.e. only during the null
window. Steady-state traffic never touches it. Its cost is exactly one
volatile read per initialization race — unmeasurable against the
construction it guards.

## Holder and enum: zero steady-state cost

The holder pays the class-init lock once, ever; later calls are a plain
static load. The enum pays class init once; later uses are a static
field read. Where they fit, both beat DCL on price and on review burden
— DCL's single volatile read is cheap, but zero plus no-subtlety is
cheaper.

## Benchmarking warnings

- Do not chase the reorder in a benchmark: the half-constructed read is
  adversarial-timing-only. Benchmarks here assert guarantees (single
  instance, `value == 42`), never the absence of a failure.
- Warm up before timing monitor vs volatile paths; cold JVM numbers mix
  compilation into the comparison.
- The 50 ms sleep in `NoSecondCheck` is a determinism wedge, not a cost
  model — never include wedged runs in timing.
