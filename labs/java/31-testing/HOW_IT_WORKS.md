# How Testing Works — Step by Step

## Step 1: Test Discovery

JUnit discovers tests at runtime through reflection. It scans the classpath for:
- Methods annotated with @Test
- Classes that match include/exclude filters (tags, custom annotations)

`java
@Test
@DisplayName("Calculates correct sum")
void addPositiveNumbers() {
    assertEquals(5, calculator.add(2, 3));
}
`

## Step 2: Test Instance Creation

For each test class, JUnit creates a test instance. By default (@TestInstance(Lifecycle.PER_METHOD)), a new instance is created for each test method. PER_CLASS creates one instance for all tests.

`java
@TestInstance(TestInstance.Lifecycle.PER_CLASS)
class MyTest { }
`

## Step 3: Lifecycle Execution

For each test method, JUnit follows this sequence:
1. Call @BeforeAll method (once per class)
2. For each test method:
   a. Create test instance (PER_METHOD mode)
   b. Resolve parameters (ExtensionContext)
   c. Call @BeforeEach method
   d. Call @Test method
   e. Call @AfterEach method
3. Call @AfterAll method (once per class)

After @BeforeEach or @AfterEach fails, the remaining lifecycle continues but the test is marked as failed.

## Step 4: Assertion Evaluation

When ssertEquals(expected, actual) runs:
1. Compute both expressions
2. Compare using .equals() (or == for primitives)
3. If mismatch: throw AssertionFailedError
4. JUnit catches the error, records the failure, and continues with remaining tests

ssertAll groups multiple assertions so all are evaluated even if some fail:
`java
assertAll("user",
    () -> assertEquals("Alice", user.getName()),
    () -> assertEquals("alice@example.com", user.getEmail())
);
`

## Step 5: Mockito Mock Creation

When a test class has @ExtendWith(MockitoExtension.class):
1. Mockito finds all @Mock fields and creates mock objects
2. For each @InjectMocks field, Mockito injects mocks via constructor, setter, or field injection (in that priority order)

`java
@Mock UserRepository repo;        // Creates a mock
@InjectMocks UserServiceImpl svc; // Injects 'repo' mock into new UserServiceImpl(repo, ...)
`

## Step 6: Stubbing

when(repo.findById(1L)).thenReturn(Optional.of(user)):
1. Mockito records a stub on the mock
2. When indById(1L) is called, Mockito intercepts and returns the recorded value
3. If called with a different argument, Mockito returns the default (empty Optional, 0, false, null)

## Step 7: Verification

erify(repo).findById(1L):
1. Mockito checks if indById(1L) was called at least once during the test
2. If not, throws TooLittleActualInvocations
3. erify(repo, times(2)) checks exact call count
4. erify(repo, never()) checks the method was never called

## Step 8: Test Summary

JUnit aggregates results: total tests, passed, failed, aborted (assumptions), and duration. Build tools (Maven Surefire, Gradle) produce XML reports consumed by CI/CD dashboards.
