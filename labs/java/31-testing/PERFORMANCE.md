# Refactoring Tests

## 1. Extract Setup to @BeforeEach

**Before:**
`java
@Test void test1() {
    Calculator c = new Calculator();
    assertEquals(5, c.add(2, 3));
}
@Test void test2() {
    Calculator c = new Calculator();
    assertEquals(0, c.subtract(2, 2));
}
`

**After:**
`java
private Calculator c;
@BeforeEach void setUp() { c = new Calculator(); }
`

## 2. Replace Repeated Assertions with Parameterized Tests

**Before:**
`java
@Test void add1() { assertEquals(2, calc.add(1, 1)); }
@Test void add2() { assertEquals(5, calc.add(2, 3)); }
@Test void add3() { assertEquals(0, calc.add(-1, 1)); }
`

**After:**
`java
@ParameterizedTest @CsvSource({"1,1,2","2,3,5","-1,1,0"})
void addTest(double a, double b, double expected) {
    assertEquals(expected, calc.add(a, b));
}
`

## 3. Remove Duplicate Assertion Logic

**Before:**
`java
@Test void add() { assertEquals(5.0, calc.add(2, 3), 0.001); }
@Test void sub() { assertEquals(1.0, calc.subtract(3, 2), 0.001); }
`

**After:**
`java
private static final double DELTA = 0.001;
// use assertEquals(expected, actual, DELTA) everywhere
`

## 4. Use Custom Assertions

`java
public static void assertUserEquals(User expected, User actual) {
    assertAll("user",
        () -> assertEquals(expected.getId(), actual.getId()),
        () -> assertEquals(expected.getEmail(), actual.getEmail())
    );
}
`

## 5. Replace Thread.sleep with Awaitility

**Before:**
`java
Thread.sleep(2000);
assertTrue(result.isReady());
`

**After:**
`java
await().atMost(2, SECONDS).until(() -> result.isReady());
`

## 6. Organize Tests with @Nested

`java
class CalculatorTest {
    @Nested class Addition { /* add tests */ }
    @Nested class Division { /* div tests */ }
    @Nested class EdgeCases { /* edge tests */ }
}
`

## 7. Name Tests Clearly

**Before:** 	est1(), 	estCalc(), checkAdd()

**After:** ddingTwoPositiveNumbersReturnsSum(), dividingByZeroThrowsException()
"@ | Set-Content -Path (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\java\31-testing "REFACTORING.md") -Encoding UTF8

@"
# Performance of Tests

## Fast Tests, Slow Tests

Test suite speed directly impacts developer productivity. A 10-minute test suite costs 30+ minutes per day of waiting.

### Typical Performance Budget

| Test Type | Count | Budget per Test | Total |
|-----------|-------|-----------------|-------|
| Unit | 1000 | 10ms | 10s |
| Integration | 100 | 1s | 100s |
| E2E | 10 | 10s | 100s |

### Measuring Test Performance

`ash
mvn test -DforkCount=4  # Parallel execution
mvn test -pl my-module   # Run only changed module
`

## Slow Test Patterns

### 1. Real I/O Instead of Mocks

Reading files, connecting to databases, or making HTTP calls in unit tests. Solution: mock all external I/O.

### 2. Thread.sleep for Async

`java
// BAD — 2s delay even if result is ready in 10ms
Thread.sleep(2000);

// GOOD — Awaitility polls efficiently
await().atMost(2, SECONDS).until(result::isReady);
`

### 3. Heavy Object Construction in @BeforeEach

Move expensive setup to @BeforeAll (static) and ensure tests don't mutate shared state.

### 4. Overuse of @BeforeAll for Data Setup

Inserting 10,000 database rows for every test class. Use minimal data per test.

## Parallel Test Execution

JUnit 5 supports parallel execution:
`properties
junit.jupiter.execution.parallel.enabled=true
junit.jupiter.execution.parallel.mode.default=same_thread
junit.jupiter.execution.parallel.mode.classes.default=concurrent
`

## Test Impact Analysis

Only run tests affected by code changes:
- Maven: mvn test -pl changed-module -am
- Gradle: gradle test --changed
- Tools: Infra-macist (Google), PIT test selection

## Benchmarking Tests

Use JUnit 5 @TestMethodOrder and @TestInstance(Lifecycle.PER_CLASS) to benchmark test performance.
