# 09 — AWS Security — Common Mistakes

## 1. Over-Engineering
Building complex abstractions before they are needed. Start simple, refactor when patterns emerge.

## 2. Ignoring Error Handling
Catching generic Exception instead of specific types. Always log context with exceptions.

## 3. Tight Coupling to Implementation
Depending on concrete classes instead of interfaces. Use dependency injection.

## 4. Missing Configuration Externalization
Hardcoding endpoints, credentials, and settings. Use environment variables and config files.

## 5. Inadequate Testing
Only testing the happy path. Test both success and failure scenarios with parameterized tests.

## 6. Ignoring Resource Cleanup
Not closing connections, streams, or threads. Use try-with-resources for AutoCloseable objects.

## 7. Premature Optimization
Optimizing code before measuring performance. Profile first, then optimize actual hot spots.

## 8. Lack of Observability
No metrics, logging, or tracing. Add structured logging and metrics endpoints from day one.

## 9. Ignoring Security
Skipping input validation, using weak authentication. Security must be a first-class concern.

## 10. Poor Configuration Management
Mixing configuration with application code. Externalize all configuration.

## 11. Missing Health Checks
Deploying without health check endpoints. Always implement /health and /ready endpoints.

## 12. Inadequate Error Responses
Returning stack traces or internal details to clients. Use structured error responses.

