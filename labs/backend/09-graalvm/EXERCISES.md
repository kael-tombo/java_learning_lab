# Exercises

## Exercise 1: Walking Skeleton
Create a minimal application demonstrating GraalVM. Add one happy path and one error path.

## Exercise 2: Configuration
Externalise the main knobs into `application.yml` and add a profile override.

## Exercise 3: Validation & Errors
Return a proper 4xx/5xx mapping with a stable error payload.

## Exercise 4: Observability
Add a Micrometer metric and a structured log line around the core operation.

## Exercise 5: Slice Test
Write a `@WebMvcTest` or equivalent slice test for the boundary.

## Exercise 6: Integration Test
Add a Testcontainers-backed integration test for the real dependency.

## Exercise 7: Failure Injection
Force a timeout/dependency failure and assert the fallback behaviour.

## Exercise 8: Benchmark
Compare sync vs async or cached vs uncached with a small load script.

## Exercise 9: Docs
Generate/verify OpenAPI (or equivalent) and add a README section.

## Exercise 10: Teardown
Add graceful shutdown and a cleanup hook; verify in tests.
