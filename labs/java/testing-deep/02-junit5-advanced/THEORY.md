# JUnit 5 Advanced -- Theoretical Foundation
## Core Concepts
### 1. Testing Fundamentals
Software testing verifies that code behaves as expected. The JUnit 5 Advanced provides a framework for writing and running tests.
### 2. Test Pyramid
- Unit Tests: Fast, isolated, cover individual components
- Integration Tests: Verify component interaction
- End-to-End Tests: Full system validation
### 3. Key Principles
- Tests should be independent and repeatable
- Test one thing at a time
- Use meaningful test names
- Tests are documentation
## Test Lifecycle
@BeforeAll -> @BeforeEach -> @Test -> @AfterEach -> @AfterAll
## Assertions
Assertions validate expected outcomes. JUnit 5 provides assertEquals, assertTrue, assertThrows, and more.
## Test Doubles
- Mock: Pre-programmed expectations
- Stub: Returns fixed values
- Spy: Wraps real object, records interactions
- Fake: Simplified implementation
