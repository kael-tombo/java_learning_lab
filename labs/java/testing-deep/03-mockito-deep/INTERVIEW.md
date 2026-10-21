# Interview Questions: Mockito Deep Dive

## Company-Specific Focus

### Google
- Mockito: mocking framework for unit testing
- Mock: @Mock annotation for creating mock objects
- Stubbing: when().thenReturn(), when().thenThrow(), when().thenAnswer()

### Microsoft
- Mockito vs Moq (.NET): similar mocking patterns
- Verification: verify() for method call verification

### Amazon
- Argument matchers: any(), eq(), anyString(), anyInt()
- Partial mocks: @Spy for partial mocking of real objects
- Mocking final classes: Mockito 2+ supports mocking final classes

### Meta
- BDD style: BDDMockito with given().willReturn()
- Answer: custom answer for complex stubbing
- MockitoJUnitRunner vs MockitoExtension (JUnit 5)

### Apple
- Mocking static methods: Mockito 3.4+ with MockedStatic
- Mocking constructors: Mockito 3.5+ with MockedConstruction
- Capturing arguments: ArgumentCaptor for verifying method arguments

### Oracle
- Mockito is the most popular Java mocking framework
- Inline mock maker: mockito-inline for final class/static mock support
- Mockito's CGLIB/ByteBuddy: proxy-based mock creation

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems — Mockito is a testing framework) |

## Real Production Scenarios
- **Uber**: Mockito mocked Redis client in unit tests — discovered a serialization bug early
- **LinkedIn**: Spy on a real service for partial mocking in integration tests

## Interview Patterns & Tips
- **Mock dependencies**: mock external services, databases, file systems
- **verify**: always verify that expected methods were called
- **ArgumentMatchers**: use eq() when mixing matchers and values
- **Don't overmock**: mock only external dependencies, not internal logic

## Deep Dive Questions
- **ByteBuddy**: How does Mockito create mock objects at runtime?
- **Inline mock maker**: How does mocking of final classes and statics work?
- **ArgumentMatcher**: How do argument matchers work internally?
- **Spy**: How does a spy differ from a mock?
- **Verification mode**: What verification modes does Mockito support?