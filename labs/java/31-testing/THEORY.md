# Testing — Theoretical Foundation

## What Is Software Testing?

Software testing is the process of verifying that a program behaves as expected under specified conditions. In Java, testing is typically automated using frameworks like JUnit and Mockito, integrated into build pipelines with Maven or Gradle.

## The Testing Pyramid

The testing pyramid describes three tiers of automated tests:

### 1. Unit Tests (Base)
Test individual components in isolation. Each test exercises one class or method, with external dependencies mocked. Fast (milliseconds), reliable, and pinpoint failures precisely.

### 2. Integration Tests (Middle)
Test interactions between components — database access, REST calls, file I/O. Slower than unit tests but catch wiring errors and contract mismatches.

### 3. End-to-End Tests (Top)
Test complete user workflows through the entire system. Slowest, most fragile, but most realistic.

## JUnit 5 Architecture

JUnit 5 consists of three modules:
- **JUnit Platform**: Foundation for launching test frameworks on the JVM
- **JUnit Jupiter**: Programming model with annotations (@Test, @BeforeEach, etc.) and assertions
- **JUnit Vintage**: Backward-compatibility engine for JUnit 4 tests

### Key Annotations

| Annotation | Scope | Purpose |
|------------|-------|---------|
| @Test | Method | Marks a test method |
| @BeforeEach | Method | Runs before each test |
| @AfterEach | Method | Runs after each test |
| @BeforeAll | Method | Runs once before all tests (must be static) |
| @AfterAll | Method | Runs once after all tests |
| @DisplayName | Method/Class | Human-readable test name |
| @Nested | Class | Groups related tests |
| @Tag | Method/Class | Filter tests by tag |
| @ParameterizedTest | Method | Runs test with multiple arguments |

### Assertions

Assertions compare actual vs expected values and fail the test if the condition is false:

`java
assertEquals(expected, actual);
assertTrue(condition);
assertFalse(condition);
assertThrows(ExpectedException.class, () -> code);
assertAll("group", () -> assertEq(a, b), () -> assertEq(c, d));
`

### Assumptions

Assumptions skip a test when a condition is not met, without marking it as failed:

`java
assumeTrue(System.getProperty("os.name").contains("Linux"));
`

## Mockito Fundamentals

Mockito creates mock objects that simulate real dependencies. Key features:

| Feature | Purpose |
|---------|---------|
| @Mock | Creates a mock instance |
| @InjectMocks | Injects mocks into the tested object |
| when(x.method()).thenReturn(v) | Stubs a method call |
| when(x.method()).thenThrow(e) | Stubs an exception |
| erify(x).method() | Verifies a method was called |
| erify(x, times(n)).method() | Verifies call count |
| doThrow(e).when(x).method() | Stubs void methods |
| @Spy | Wraps a real object, tracking calls |
| @Captor | Captures argument values |

## TDD Cycle

1. **Red**: Write a failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Improve code while keeping tests green

## Parameterized Tests

Run the same test logic with different inputs:

`java
@ParameterizedTest
@ValueSource(ints = {1, 2, 3})
@CsvSource({"1,2,3", "4,5,9"})
@MethodSource("dataProvider")
void testMethod(int input) { ... }
`

## Test Coverage

Coverage metrics measure which code paths are exercised:
- **Line coverage**: Percentage of source lines executed
- **Branch coverage**: Percentage of if/else branches taken
- **Mutation coverage**: Percentage of mutants (syntactic changes) killed by tests

Tools: JaCoCo, Cobertura, OpenClover. Target: 80%+ branch coverage for production code.
