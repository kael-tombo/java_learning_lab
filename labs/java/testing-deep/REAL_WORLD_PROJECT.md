# Real-World Project — Deep Java Testing (testing-deep)

Production-style build around JUnit5, Mockito, AssertJ, Testcontainers: design, scale, operate.

## Problem statement
Design a service/demo where JUnit5 lifecycle & extensions, parameterized tests, Mockito stubbing/verification are load-bearing. Must handle restarts, bad input, and load.

## Architecture
- `JUnit5 lifecycle & extensions` → component + owner + SLO.
- `parameterized tests` → component + owner + SLO.
- `Mockito stubbing/verification` → component + owner + SLO.
- `AssertJ fluent assertions` → component + owner + SLO.
- `Testcontainers` → component + owner + SLO.

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
- https://docs.oracle.com/en/java/javase/17/docs/api/java.base/java/util/concurrent/package-summary.html
- https://junit.org/junit5/docs/current/user-guide/
- https://openjdk.org/projects/jmh/

## Deliverables
- Repo + tests + benchmark + 1-page ops note.
Extension 0: scale JUnit5 lifecycle & extensions under load.
Extension 1: scale parameterized tests under load.
Extension 2: scale Mockito stubbing/verification under load.
Extension 3: scale AssertJ fluent assertions under load.
Extension 4: scale Testcontainers under load.
Extension 5: scale mutation testing under load.
Extension 6: scale test slices under load.
Extension 7: scale flaky-test strategy under load.
Extension 8: scale JUnit5 lifecycle & extensions under load.
Extension 9: scale parameterized tests under load.
Extension 10: scale Mockito stubbing/verification under load.
Extension 11: scale AssertJ fluent assertions under load.
Extension 12: scale Testcontainers under load.
Extension 13: scale mutation testing under load.
Extension 14: scale test slices under load.
Extension 15: scale flaky-test strategy under load.
Extension 16: scale JUnit5 lifecycle & extensions under load.
Extension 17: scale parameterized tests under load.
Extension 18: scale Mockito stubbing/verification under load.
Extension 19: scale AssertJ fluent assertions under load.
Extension 20: scale Testcontainers under load.
Extension 21: scale mutation testing under load.
Extension 22: scale test slices under load.
Extension 23: scale flaky-test strategy under load.
Extension 24: scale JUnit5 lifecycle & extensions under load.
Extension 25: scale parameterized tests under load.
Extension 26: scale Mockito stubbing/verification under load.
Extension 27: scale AssertJ fluent assertions under load.
Extension 28: scale Testcontainers under load.
Extension 29: scale mutation testing under load.
Extension 30: scale test slices under load.
Extension 31: scale flaky-test strategy under load.
Extension 32: scale JUnit5 lifecycle & extensions under load.
Extension 33: scale parameterized tests under load.
Extension 34: scale Mockito stubbing/verification under load.
Extension 35: scale AssertJ fluent assertions under load.
Extension 36: scale Testcontainers under load.
Extension 37: scale mutation testing under load.
Extension 38: scale test slices under load.
Extension 39: scale flaky-test strategy under load.
Extension 40: scale JUnit5 lifecycle & extensions under load.
Extension 41: scale parameterized tests under load.
Extension 42: scale Mockito stubbing/verification under load.
Extension 43: scale AssertJ fluent assertions under load.
Extension 44: scale Testcontainers under load.
Extension 45: scale mutation testing under load.
Extension 46: scale test slices under load.
Extension 47: scale flaky-test strategy under load.
Extension 48: scale JUnit5 lifecycle & extensions under load.
Extension 49: scale parameterized tests under load.
Extension 50: scale Mockito stubbing/verification under load.
Extension 51: scale AssertJ fluent assertions under load.
Extension 52: scale Testcontainers under load.
Extension 53: scale mutation testing under load.
Extension 54: scale test slices under load.
Extension 55: scale flaky-test strategy under load.
Extension 56: scale JUnit5 lifecycle & extensions under load.
Extension 57: scale parameterized tests under load.
Extension 58: scale Mockito stubbing/verification under load.
Extension 59: scale AssertJ fluent assertions under load.
Extension 60: scale Testcontainers under load.
Extension 61: scale mutation testing under load.
Extension 62: scale test slices under load.
Extension 63: scale flaky-test strategy under load.
Extension 64: scale JUnit5 lifecycle & extensions under load.
Extension 65: scale parameterized tests under load.
Extension 66: scale Mockito stubbing/verification under load.
Extension 67: scale AssertJ fluent assertions under load.
Extension 68: scale Testcontainers under load.
Extension 69: scale mutation testing under load.
Extension 70: scale test slices under load.
Extension 71: scale flaky-test strategy under load.
Extension 72: scale JUnit5 lifecycle & extensions under load.
Extension 73: scale parameterized tests under load.
Extension 74: scale Mockito stubbing/verification under load.
