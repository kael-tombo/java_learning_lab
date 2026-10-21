# Interview Questions: JUnit 5 Fundamentals

## Company-Specific Focus

### Google
- JUnit 5: @Test, lifecycle (@BeforeEach, @AfterEach, @BeforeAll, @AfterAll)
- Assertions: assertEquals, assertThrows, assertAll, assertTimeout
- Assumptions: assumeTrue, assumeFalse for conditional test execution

### Microsoft
- JUnit 5 vs .NET NUnit/MSTest: similar annotations and assertions
- Display names: @DisplayName for readable test names

### Amazon
- Test lifecycle: @BeforeAll for expensive setup (database connections)
- Nested tests: @Nested for hierarchical test organization
- Tagging: @Tag for test categorization and filtering

### Meta
- AssertJ assertions: fluent assertions
- Parameterized tests: @ParameterizedTest with @ValueSource, @CsvSource
- Repeated tests: @RepeatedTest for flaky test detection

### Apple
- Test interfaces: @TestInstance for lifecycle per class vs per method
- Timeout: @Timeout for test execution time limit
- Disabled: @Disabled for skipping tests

### Oracle
- JUnit 5 architecture: JUnit Platform + JUnit Jupiter + JUnit Vintage
- Extension model: @ExtendWith for registering extensions
- TestEngine: SPI for implementing test engines

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (Testing concepts apply to all LC problems) |
| 146 LRU Cache | Medium | Google, Amazon, Apple | Unit testing cache behavior |

## Real Production Scenarios
- **Slack**: Flaky test identified with @RepeatedTest(100) — sporadic failure due to race condition
- **LinkedIn**: @Nested tests for organizing integration test hierarchy

## Interview Patterns & Tips
- **FIRST**: Fast, Isolated, Repeatable, Self-validating, Timely
- **@Nested**: organize tests by feature or scenario
- **@ParameterizedTest**: reduce boilerplate, increase coverage
- **assertAll**: group related assertions to see all failures

## Deep Dive Questions
- **JUnit 5 architecture**: How does the platform/engine separation work?
- **Extension model**: How do extensions work (BeforeEachCallback, AfterEachCallback, etc.)?
- **Discovery**: How are tests discovered by the JUnit Platform?
- **Execution**: How does JUnit execute tests in parallel?
- **Report**: How does JUnit generate test execution reports?