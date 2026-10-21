# Testcontainers -- Test Performance
## Performance Considerations
### Fast Tests
Unit tests should run in milliseconds.
### Parallel Execution
Use @Execution(ExecutionMode.CONCURRENT) for parallel tests.
### Container Startup
Testcontainers reuse containers across tests for speed.
