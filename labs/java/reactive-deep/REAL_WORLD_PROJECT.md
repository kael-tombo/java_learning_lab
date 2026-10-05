# Real-World Project — Reactive Java Deep Dive (reactive-deep)

Production-style build around Reactor, RxJava, Flow API, backpressure: design, scale, operate.

## Problem statement
Design a service/demo where Publisher/Subscriber, Flux/Mono, backpressure strategies are load-bearing. Must handle restarts, bad input, and load.

## Architecture
- `Publisher/Subscriber` → component + owner + SLO.
- `Flux/Mono` → component + owner + SLO.
- `backpressure strategies` → component + owner + SLO.
- `schedulers` → component + owner + SLO.
- `error handling` → component + owner + SLO.

## Milestones (4)
1. Slice: happy path + test.
2. Harden: timeouts, retries, validation.
3. Observe: logs/metrics/JFR + dashboard.
4. Scale: benchmark + tune one bottleneck.

## Ops checklist
- [ ] Dockerfile + health check
- [ ] Load test (k6/JMeter) with p99
- [ ] Runbook: top-3 failures + mitigations

## Interview story
Prepare STAR: problem → approach → metric → lesson.

## Sourced field notes (fetched Oct 2026 — verify before citing)
- https://docs.oracle.com/en/java/javase/17/docs/api/
- https://openjdk.org/jeps/401 (value classes discussion)
- https://openjdk.org/projects/jmh/

## Deliverables
- Repo + tests + benchmark + 1-page ops note.
Extension 0: scale Publisher/Subscriber under load.
Extension 1: scale Flux/Mono under load.
Extension 2: scale backpressure strategies under load.
Extension 3: scale schedulers under load.
Extension 4: scale error handling under load.
Extension 5: scale testing with StepVerifier under load.
Extension 6: scale R2DBC/reactive web under load.
Extension 7: scale virtual threads vs reactive under load.
Extension 8: scale Publisher/Subscriber under load.
Extension 9: scale Flux/Mono under load.
Extension 10: scale backpressure strategies under load.
Extension 11: scale schedulers under load.
Extension 12: scale error handling under load.
Extension 13: scale testing with StepVerifier under load.
Extension 14: scale R2DBC/reactive web under load.
Extension 15: scale virtual threads vs reactive under load.
Extension 16: scale Publisher/Subscriber under load.
Extension 17: scale Flux/Mono under load.
Extension 18: scale backpressure strategies under load.
Extension 19: scale schedulers under load.
Extension 20: scale error handling under load.
Extension 21: scale testing with StepVerifier under load.
Extension 22: scale R2DBC/reactive web under load.
Extension 23: scale virtual threads vs reactive under load.
Extension 24: scale Publisher/Subscriber under load.
Extension 25: scale Flux/Mono under load.
Extension 26: scale backpressure strategies under load.
Extension 27: scale schedulers under load.
Extension 28: scale error handling under load.
Extension 29: scale testing with StepVerifier under load.
Extension 30: scale R2DBC/reactive web under load.
Extension 31: scale virtual threads vs reactive under load.
Extension 32: scale Publisher/Subscriber under load.
Extension 33: scale Flux/Mono under load.
Extension 34: scale backpressure strategies under load.
Extension 35: scale schedulers under load.
Extension 36: scale error handling under load.
Extension 37: scale testing with StepVerifier under load.
Extension 38: scale R2DBC/reactive web under load.
Extension 39: scale virtual threads vs reactive under load.
Extension 40: scale Publisher/Subscriber under load.
Extension 41: scale Flux/Mono under load.
Extension 42: scale backpressure strategies under load.
Extension 43: scale schedulers under load.
Extension 44: scale error handling under load.
Extension 45: scale testing with StepVerifier under load.
Extension 46: scale R2DBC/reactive web under load.
Extension 47: scale virtual threads vs reactive under load.
Extension 48: scale Publisher/Subscriber under load.
Extension 49: scale Flux/Mono under load.
Extension 50: scale backpressure strategies under load.
Extension 51: scale schedulers under load.
Extension 52: scale error handling under load.
Extension 53: scale testing with StepVerifier under load.
Extension 54: scale R2DBC/reactive web under load.
Extension 55: scale virtual threads vs reactive under load.
Extension 56: scale Publisher/Subscriber under load.
Extension 57: scale Flux/Mono under load.
Extension 58: scale backpressure strategies under load.
Extension 59: scale schedulers under load.
Extension 60: scale error handling under load.
Extension 61: scale testing with StepVerifier under load.
Extension 62: scale R2DBC/reactive web under load.
Extension 63: scale virtual threads vs reactive under load.
Extension 64: scale Publisher/Subscriber under load.
Extension 65: scale Flux/Mono under load.
Extension 66: scale backpressure strategies under load.
Extension 67: scale schedulers under load.
Extension 68: scale error handling under load.
Extension 69: scale testing with StepVerifier under load.
Extension 70: scale R2DBC/reactive web under load.
Extension 71: scale virtual threads vs reactive under load.
Extension 72: scale Publisher/Subscriber under load.
Extension 73: scale Flux/Mono under load.
Extension 74: scale backpressure strategies under load.
