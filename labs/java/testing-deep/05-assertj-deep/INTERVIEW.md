# Interview Questions: AssertJ Deep Dive

## Company-Specific Focus

### Google
- AssertJ: fluent assertions for Java
- Basic assertions: assertThat(value).isEqualTo(), isNotNull(), isIn()
- Custom assertions: extending AbstractAssert for domain-specific assertions

### Microsoft
- AssertJ vs .NET FluentAssertions
- Soft assertions: SoftAssertions for collecting multiple assertion failures

### Amazon
- Collection assertions: contains, containsExactly, containsOnly, hasSize
- Map assertions: containsKey, containsValue, hasEntrySatisfying
- Exception assertions: assertThatThrownBy, assertThatExceptionOfType

### Meta
- FlatMap extraction: extracting values from objects for assertions
- Filtering: filteredOn for filtering collections in assertions
- Condition: custom conditions for complex assertions

### Apple
- Date/Time assertions: LocalDate, LocalDateTime assertions
- Optional assertions: isPresent, contains, isEmpty
- File assertions: exists, isDirectory, content comparison

### Oracle
- AssertJ is a third-party library widely used in the Java ecosystem
- Improving test readability: fluent API
- Integrated with JUnit 5 and TestNG

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems — AssertJ is a testing library) |

## Real Production Scenarios
- **Netflix**: Custom AssertJ assertions for domain objects improved test readability by 50%
- **LinkedIn**: SoftAssertions collected all failures in integration tests — no early exit

## Interview Patterns & Tips
- **Fluent**: assertThat(actual).isEqualTo(expected).isNotNull()
- **Soft**: collect all failures before reporting
- **Custom**: extend AbstractAssert for domain models
- **Extracting**: extracting fields for specific assertions

## Deep Dive Questions
- **AssertJ vs Hamcrest**: How does AssertJ compare to Hamcrest matchers?
- **Soft assertions**: How do SoftAssertions collect failures?
- **Custom assertion**: How to create a domain-specific assertion class?
- **Condition**: How to create a custom Condition?
- **Java 8 integration**: How does AssertJ work with Optional and Stream?