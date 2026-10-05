# Mini Project: CQRS with Axon Framework

## Goal
Build a small, runnable CQRS with Axon Framework service that demonstrates the core happy path.

## Requirements
- Java 17+, Maven, Spring Boot 3.x
- One controller, one service, one dependency (or in-memory substitute)
- One happy-path endpoint and one error-path endpoint
- At least one metric and one structured log line

## Skeleton
```java
@SpringBootApplication
public class App {
    public static void main(String[] args) {
        SpringApplication.run(App.class, args);
    }
}
```

## Steps
1. Model the resource(s) as a small domain object.
2. Create the service with a single public operation.
3. Add the controller mapping to the status codes.
4. Add a Micrometer counter on the happy path.
5. Write a slice test and an integration test.

## Done when
- The endpoint returns 200 on success and a stable error body on failure.
- Tests pass in CI.
- The README explains how to run it.
