# Architectural Implications of Testing

## Testability Drives Architecture

Good architecture enables good testing. The need for testability pushes design toward:

### Dependency Injection
`java
// Hard to test — hardcoded dependency
class Service {
    private Database db = new Database();
}

// Easy to test — injected dependency
class Service {
    private final Database db;
    Service(Database db) { this.db = db; }
}
`

### Interface Segregation
Narrow interfaces are easy to mock. Wide interfaces with 20 methods require stubbing every method.

### Single Responsibility
Classes with one responsibility are trivial to test. Classes doing 5 things require 5x the tests.

### Hexagonal Architecture
Ports and adapters architecture (ports = interfaces, adapters = implementations) makes every external dependency mockable.

## Test Organization

`
src/
├── main/java/com/app/
│   ├── service/
│   ├── repository/
│   └── domain/
└── test/java/com/app/
    ├── service/    # Mirror of main structure
    ├── repository/
    └── domain/
`

## Test Doubles

| Double | Behavior | When to Use |
|--------|----------|-------------|
| Dummy | No behavior, just fills params | Required constructor args |
| Fake | Simplified working implementation | In-memory database |
| Stub | Returns canned answers | Query methods |
| Mock | Verifies interactions | Command methods |
| Spy | Wraps real object, records calls | Legacy code, partial mocking |

## Integration Test Architecture

`
@Testcontainers
  └── DatabaseContainer (PostgreSQL)
  └── QueueContainer (RabbitMQ)
      └── @SpringBootTest
          └── Service Layer
          └── Repository Layer
`

## CI/CD Pipeline Integration

`
Push → Build → Unit Tests → Integration Tests → Coverage Gate → Deploy
        (mvn compile)  (mvn test)  (mvn verify)    (JaCoCo)     (deploy)
`

Each stage gates the next. A failing test blocks deployment.
