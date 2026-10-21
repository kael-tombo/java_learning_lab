# Testcontainers -- How It Works
## How Testing Frameworks Work
### Test Discovery
JUnit 5 discovers tests by scanning classpath for @Test annotations.
### Test Execution
Each test runs in a new test instance by default.
### Assertion Evaluation
Assertions throw AssertionError on failure, caught by the test runner.
