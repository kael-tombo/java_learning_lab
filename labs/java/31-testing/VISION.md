# VISION — Testing (JUnit 5 + Doubles + Containers)

## Vision Statement
**Tests are executable specifications** — a fast unit ring, honest slice
tests, and a thin E2E tip let you refactor at speed and deploy on green
without flaky-test roulette.

---

## Mental Models
### 1. Pyramid, Not Ice-Cream Cone
Many fast unit tests, fewer slice/integration, very few E2E. If E2E dominate,
feedback is slow and failures vague — push logic down to unit-testable code.
### 2. AAA + One Reason to Fail
Arrange-Act-Assert, single behavior per test, `@DisplayName` as spec.
Parametrized tests (`@ParameterizedTest`) cover edges without duplication.
### 3. Doubles Have Jobs
Stub returns data, mock verifies interaction, fake runs real logic in-memory.
Mock boundaries (ports), not internals — over-mocking cements bad design.
### 4. Integration Proves Wiring
Testcontainers (Postgres/Kafka) + `@DataJpaTest`/slice tests prove SQL,
migrations, and config. Tag slow tests (`@Tag("slow")`) and gate PRs on fast
ring only.

---

## Decision Framework
| Question | Rule |
|----------|------|
| What to unit-test? | Pure logic, mappers, validators, state machines |
| Mock or real? | Mock external ports; real for owned logic |
| Flaky test? | Quarantine + fix (clock/random/ordering), never retry-blind |
| Coverage target? | Mutation-relevant paths, not % theater |
| Slow suite? | Split fast/slow; parallelize, container-reuse |

---

## Career Trajectory
- **L1:** JUnit5 lifecycle, assertions, Mockito basics, test naming.
- **L2:** Parametrized, slices, Testcontainers, WireMock, Awaitility.
- **L3:** Mutation testing (PIT), contract tests, flake elimination.
- **L4:** Quality strategy (gates, coverage policy, test-data platform).

---

## 4-Week Path
```
W1: JUnit5 + AssertJ + Mockito; AAA and naming.
W2: Slice tests (DataJpa/WebMvc), WireMock, time control.
W3: Testcontainers Postgres/Kafka; tagging + parallel runs.
W4: PIT mutation kata + flake-hunt capstone.
```
## Success Metrics
- [ ] PR ring < 3 min; flake rate < 1%
- [ ] Mutation score gates meaningful code
- [ ] Every bug gets a regression test first
