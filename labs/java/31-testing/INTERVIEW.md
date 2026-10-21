# Interview Questions: Testing

## Company-Specific Focus

### Google
- Unit testing with JUnit 5: @Test, assertions, lifecycle hooks (@BeforeEach, @AfterEach)
- Mocking with Mockito: when/thenReturn, verify, argument matchers
- Integration testing: how to test production scenarios

### Microsoft
- Java testing vs C# testing: JUnit vs NUnit/MSTest frameworks
- Mocking with Mockito vs Moq (C#)
- Parameterized tests: grouping similar test variations

### Amazon
- Integration tests for the service in the deployment pipeline
- TestContainers: database/integration tests using containerized services
- Chaos engineering: testing for resilience with fault injection

### Meta
- Test coverage: what matters at scale vs vanity metrics
- Property based testing using jqwik or quickcheck
- Fuzz testing for security related APIs

### Apple
- Unit vs. integration tests in an iOS context
- Using test fixtures and dependency injection
- Stubbing services

### Oracle
- JUnit 5 architecture: JUnit Platform, Jupiter, Vintage
- AssertJ for fluent assertions
- Test lifecycle and its relation to the JVM

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (Testing concepts apply to all LC problems) |
| 146 LRU Cache | Medium | Google, Apple, Amazon | Test cache eviction and ordering |
| 380 Insert Delete GetRandom O(1) | Medium | Amazon, Apple, Google | Test random distribution |
| 208 Implement Trie | Medium | Google, Amazon | Test all word operations |
| 211 Design Add and Search Words Data Structure | Medium | Amazon, Google | Test edge cases with patterns |

## Real Production Scenarios
- **Slack**: A flaky test failing in CI due to a race condition — stabilized by ordering the operation
- **Uber**: Mocking a third-party service failed due to rate limiting — mock expectations changed
- **Netflix**: TestContainers migration from a local database to Docker based reduced flaky tests by 90%

## Interview Patterns & Tips
- **FIRST principles**: Fast, Isolated, Repeatable, Self-validating, Timely
- **Test one thing per test**: descriptive name, single assertion
- **Mock external dependencies**: databases, network services, file systems
- **Avoid test interdependence**: tests should run in any order

## Deep Dive Questions
- **JVM**: How does JUnit discover tests? Uses reflection for @Test annotations
- **Mockito**: How does Mockito create mocks? ByteBuddy generates a subclass at runtime
- **Performance**: How many tests can be run per second in the JVM?
- **Integration tests**: How to manage lifecycle with TestContainers?
- **Java 21+**: Virtual threads and testing — tests for concurrency correctness?