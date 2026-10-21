# Interview Questions: Best Practices

## Company-Specific Focus

### Google
- Effective Java: Joshua Bloch's rules practiced at Google
- Code review checklist: style, performance, concurrency, security
- Builder pattern, dependency injection, immutability
- Error handling: Google's approach to checked vs unchecked exceptions

### Microsoft
- Java best practices in enterprise development
- Design patterns in Java: Singleton, Factory, Strategy, Observer
- Writing testable code: dependency injection, mockable interfaces

### Amazon
- Code quality metrics: maintainability, cyclomatic complexity, test coverage
- Immutable objects: the benefits for multithreaded microservices
- Code review: performance considerations for distributed systems

### Meta
- Clean code: readable, maintainable, and performant
- Concurrency best practices: thread safety in shared data structures
- Using Optional correctly: avoiding Optional fields

### Apple
- Favoring immutability for concurrent code
- Using records for value objects
- Avoiding unnecessary object creation

### Oracle
- Java Language Specification and Java API documentation
- Following Java naming conventions
- The Java Code Conventions document

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (Best practices apply to all coding problems) |
| 146 LRU Cache | Medium | Google, Apple, Amazon | Design best practices in cache |
| 208 Implement Trie | Medium | Amazon, Google | Clean class design |

## Real Production Scenarios
- **Amazon**: A mutable static variable caused a production outage — not following immutability best practices
- **Google**: Without using try-with-resources, a database connection leaked in a microservice
- **Slack**: Not using generics caused a ClassCastException in production

## Interview Patterns & Tips
- **Immutability**: Use final fields, records, and unmodifiable collections
- **Error handling**: Fail fast for programming errors, handle gracefully for recoverable issues
- **Documentation**: Javadoc for public APIs, comments for non-obvious logic
- **Testing**: Write testable code from the start

## Deep Dive Questions
- **Immutability**: How does immutability help with thread safety?
- **Defensive copies**: When should you create defensive copies?
- **equals/hashCode**: The contract and implementation best practices
- **Serialization**: What are best practices for serializable classes?
- **Performance**: What are the best practices for writing high-performance Java code?