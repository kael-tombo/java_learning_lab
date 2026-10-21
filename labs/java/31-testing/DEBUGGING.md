# Debugging Testing Failures

## Reading Test Failure Output

JUnit failures show:
`
CalculatorTest.addPositiveNumbers:20 expected: <5> but was: <4>
`
The format: ClassName.methodName:lineNumber expected: <V> but was: <A>

## Debugging Flaky Tests

Flaky tests pass sometimes, fail other times. Common causes:

| Cause | Fix |
|-------|-----|
| Shared mutable state | Isolate per test with @BeforeEach |
| Timing issues (async) | Use Awaitility or CountDownLatch |
| Thread ordering | Use deterministic executor |
| Date/time dependency | Use Clock injection |
| Randomness | Use fixed seed in tests |

## Debugging Mockito Failures

### "Wanted but not invoked"
Your code did not call the expected method. Check:
- Is the code path executed? (print or debug)
- Is the correct mock injected?
- Are argument matchers matching?

### "Unnecessary stubbing"
A stub was created but never used. Remove it or add lenient():

`java
lenient().when(repo.findById(99L)).thenReturn(Optional.empty());
`

### "Argument mismatch"
The actual arguments don't match matchers:
`java
// BAD: mixed matchers and raw values
verify(repo).findById(eq(1L), "test"); // Fails — all or nothing

// GOOD
verify(repo).findById(eq(1L), eq("test"));
`

## Debugging Slow Tests

Profile with @TestMethodOrder to find slow tests:

`java
@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class SlowTest {
    @Test @Order(1) void fastTest() { }
    @Test @Order(2) void slowTest() { }
}
`

## Debugging with Breakpoints

Set breakpoints inside test methods to inspect state. Most IDEs support "Debug as Test" — run the test in debug mode and step through.
