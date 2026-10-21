# Testing — Visual Guide

## ASCII Diagram: Testing Pyramid

`
              /\             
             /  \            End-to-End (Slow, Few)
            /    \           
           /      \          
          /--------\         
         /  Integr  \        Integration (Medium)
        /    ation    \      
       /--------------\     
      /   Unit Tests    \    Unit (Fast, Many)
     /____________________\  
`

## ASCII Diagram: JUnit Lifecycle

`
Class Level:
  [@BeforeAll] ──┐
                 ├── Test 1: [@BeforeEach] → [@Test] → [@AfterEach]
                 ├── Test 2: [@BeforeEach] → [@Test] → [@AfterEach]
                 ├── Test 3: [@BeforeEach] → [@Test] → [@AfterEach]
                 └── [@AfterAll]
`

## ASCII Diagram: Mockito Stubbing

`
@Mock UserRepository repo
                        │
   when(repo.findById(id)).thenReturn(user)
                        │
   Service.call() ──► repo.findById(42)
                        │
              ┌─────────┴──────────┐
              ▼                    ▼
          Stub found?         No stub?
              │                    │
         Return(user)       Return(default)
                                  │
                            Optional.empty()
`

## ASCII Diagram: TDD Cycle

`
    ┌─────────────┐
    │  Write Test  │  (RED — test fails)
    └──────┬───────┘
           │
           ▼
    ┌─────────────┐
    │ Write Code   │  (GREEN — test passes)
    └──────┬───────┘
           │
           ▼
    ┌─────────────┐
    │  Refactor    │  (Code improved, tests still pass)
    └──────┬───────┘
           │
           ▼
    ┌─────────────┐
    │  Repeat      │  (Next feature/behavior)
    └─────────────┘
`

## ASCII Diagram: Assertions Flow

`
assertEquals(expected, actual)
         │
   ┌─────┴─────┐
   ▼           ▼
null?        Compare
   │         .equals()
   ├── both null → PASS
   ├── one null → FAIL
   └── both non-null → compare
                          │
                    ┌─────┴─────┐
                    ▼           ▼
                  Equal?     Not equal?
                    │           │
                  PASS        FAIL
`
"@ | Set-Content -Path (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\java\31-testing "VISUAL_GUIDE.md") -Encoding UTF8

@"
# Testing — Code Deep Dive

## Deep Dive: CalculatorTest

`java
@BeforeEach
void setUp() {
    calculator = new Calculator();
}
`
This runs before every test, ensuring each test starts with a fresh Calculator. This prevents test order dependencies.

### Testing Exceptions

`java
@Test
void divideByZero() {
    assertThrows(ArithmeticException.class, () -> calculator.divide(1, 0));
}
`
ssertThrows asserts that the code throws exactly ArithmeticException (or a subclass). The lambda is the code under test. If no exception is thrown, the test fails.

### Parameterized Tests with @CsvSource

`java
@ParameterizedTest
@CsvSource({
    "1, 1, 2",
    "10, 20, 30",
    "-5, 5, 0"
})
void addParameterized(double a, double b, double expected) {
    assertEquals(expected, calculator.add(a, b), 1e-9);
}
`
Each CSV line is parsed and passed as arguments. This tests 3 scenarios with 1 method instead of 3.

## Deep Dive: UserServiceTest

### Mock Setup

`java
@Mock private UserRepository repository;
@Mock private NotificationService notificationService;
@InjectMocks private UserServiceImpl userService;
`
MockitoExtension (via @ExtendWith) processes these annotations before tests run. @InjectMocks creates UserServiceImpl and injects the @Mock fields into its constructor.

### Stubbing with Return Values

`java
when(repository.findById(1L)).thenReturn(Optional.of(testUser));
`
This creates a stub: when indById(1L) is called, return Optional.of(testUser). Any other argument returns Optional.empty() (default for Optional).

### Verifying Interactions

`java
verify(notificationService).send("alice@example.com", "Welcome!");
`
This verifies that send was called exactly once with the given arguments. It's the most powerful Mockito feature — it tests that your code *interacted* correctly with its dependencies, not just that it returned the right value.

### Ensuring a Method Was NOT Called

`java
verify(notificationService, never()).send(anyString(), anyString());
`
Use 
ever() to verify that a code path does NOT trigger a side effect — critical for testing conditional logic.

## Deep Dive: IntegrationTest

Integration tests use real filesystem operations:

`java
@BeforeAll
void setupEnvironment() throws IOException {
    tempDir = Files.createTempDirectory("integration-test-");
}
`
Real temp directories, real file writes, real I/O. This tests the full stack: Java I/O APIs, filesystem permissions, disk space, etc.

### Test Lifecycle Hooks

`java
@BeforeEach
void logTestStart(TestInfo info) {
    appendLog("START: " + info.getDisplayName());
}
`
TestInfo is injected automatically by JUnit. It provides the test name, tags, and display name.
