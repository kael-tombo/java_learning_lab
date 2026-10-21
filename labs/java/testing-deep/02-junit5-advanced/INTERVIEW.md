# Interview Questions: JUnit 5 Advanced

## Company-Specific Focus

### Google
- Parameterized tests: @CsvSource, @MethodSource, @EnumSource, @ArgumentsSource
- Custom arguments providers: implementing ArgumentsProvider interface
- Parameterized test lifecycle: how parameters are resolved

### Microsoft
- Dynamic tests: @TestFactory for generating tests at runtime
- DynamicNode: DynamicTest, DynamicContainer for structured dynamic tests

### Amazon
- Test templates: @TestTemplate for test invocation customization
- Test instance: @TestInstance(Lifecycle.PER_CLASS) for shared state
- Parallel execution: @Execution(ExecutionMode.CONCURRENT) for test parallelism

### Meta
- Extension model: @RegisterExtension for programmatic extension registration
- Parameter resolvers: custom ParameterResolver for injecting parameters
- Conditional execution: @EnabledOnOs, @DisabledOnJre, @EnabledIf

### Apple
- Test interfaces: @TestInterface for reusable test contracts
- Nested tests: deep nesting for complex test hierarchies
- Tag filtering: running specific tagged tests

### Oracle
- JUnit 5 extensions: BeforeAllCallback, AfterEachCallback, ParameterResolver, etc.
- TestWatcher: extension for test result tracking
- Lifecycle support: @BeforeAll, @AfterAll default to per-method lifecycle

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems — advanced JUnit 5 features) |

## Real Production Scenarios
- **Netflix**: Dynamic tests for data-driven test suites — 1000+ test cases from a single test factory
- **LinkedIn**: Custom ParameterResolver for injecting authenticated user context

## Interview Patterns & Tips
- **@MethodSource**: for complex argument objects
- **@TestFactory**: generating tests at runtime
- **@TestTemplate**: for each invocation with different context
- **Extension model**: most powerful feature of JUnit 5

## Deep Dive Questions
- **ArgumentResolver**: How to create a custom ParameterResolver?
- **DynamicTest**: How does @TestFactory generate dynamic tests?
- **Parallel execution**: How does JUnit 5 handle concurrent test execution?
- **Extensions**: How do JUnit 5 extensions discover test lifecycles?
- **TestWatcher**: How to track test pass/fail status in extensions?