# Interview Questions: Testcontainers

## Company-Specific Focus

### Google
- Testcontainers: testing with real database instances in Docker containers
- @Testcontainers: JUnit 5 extension
- @Container: field/method level container declaration

### Microsoft
- Testcontainers vs Azure Test Plans
- Database testing: PostgreSQL, MySQL, Oracle, SQL Server containers

### Amazon
- Integration testing: real AWS services with LocalStack containers
- Docker in CI: running Testcontainers in CI/CD pipelines
- Container lifecycle: singleton containers for performance

### Meta
- Wait strategies: wait for container to be ready
- Static containers: sharing containers across tests with @Container(shared = true)
- Network modes: container networking for multi-container tests

### Apple
- Testcontainers for macOS: Docker Desktop required
- Lightweight containers: Alpine-based images for fast startup

### Oracle
- Testcontainers supports Oracle XE database
- JDBC URL: using Testcontainers JDBC proxy for automated database provisioning
- Module support: testcontainers modules for specific services

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems — Testcontainers is an integration testing tool) |

## Real Production Scenarios
- **Netflix**: Testcontainers for database migration testing — catching schema drift before deployment
- **LinkedIn**: Integration tests with Kafka containers validated event processing correctly

## Interview Patterns & Tips
- **Real instances**: Testcontainers provide real database instances, not mocks
- **Singleton containers**: share containers across tests for performance
- **Docker in CI**: requires Docker socket in CI/CD environment
- **Cleanup**: containers are automatically cleaned up after tests

## Deep Dive Questions
- **Container lifecycle**: How does Testcontainers manage container startup and shutdown?
- **Docker integration**: How does Testcontainers interact with the Docker daemon?
- **Wait strategy**: What wait strategies does Testcontainers support?
- **Database testing**: How does Testcontainers work with Flyway/Liquibase migrations?
- **Module API**: How do specialized containers (PostgreSQL, Kafka) extend the base container?