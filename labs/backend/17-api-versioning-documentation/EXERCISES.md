# Exercises: API Versioning & Documentation

## Exercise 1: Version Negotiation Filter

**Objective**: Implement header-based version routing with a servlet filter.

### Task
1. Create a `OncePerRequestFilter` reading the `Api-Version` header
2. If missing, default to `v1`; if unknown (e.g. `v99`), respond `400` with a
   JSON error body listing supported versions
3. Register the filter before Spring MVC's `DispatcherServlet`
4. Expected observation: same URL returns different payloads per header value

## Exercise 2: Sunset Headers

**Objective**: Signal deprecation machine-readably.

### Task
1. In the v1 controller advice, add headers:
   `Deprecation: true`, `Sunset: Wed, 01 Jul 2026 00:00:00 GMT`,
   and `Link: </v2/users>; rel="successor-version"`
2. Hit `/v1/users` with curl -v and confirm all three headers appear
3. Expected observation: headers present only on v1 paths, not v2

## Exercise 3: Breaking-Change Detector

**Objective**: Catch accidental breaking changes in CI.

### Task
1. Check in the last-released `openapi.json` as `openapi-baseline.json`
2. Add the `openapi-diff` Maven goal (or `oasdiff`) to the build
3. Remove a field from a response DTO and run the build
4. Expected observation: build fails with a diff report listing the removal

## Exercise 4: Client Contract Test

**Objective**: Prove the server still honors the published contract.

### Task
1. Write a Pact (or Spring Cloud Contract) test that starts from the OpenAPI
   spec, not from the server mocks
2. Generate the consumer stub with `openapi-generator` in `webclient` mode
3. Call the running app via `MockMvc` backed by the generated client
4. Expected observation: renaming a JSON property server-side fails the test
   at the deserialization step

## Exercise 5: Default-Version Pinning

**Objective**: Make unversioned traffic explicit.

### Task
1. Add a property `api.default-version=v1`
2. Reject unversioned requests (no path prefix, no header) with `400` unless
   the property is explicitly opted in
3. Flip the property to `v2` in application-prod.yml
4. Expected observation: curl with no version info now fails fast instead of
   silently landing on whatever happens to be default

## Exercise 6: Documentation Drift Audit

**Objective**: Detect when annotations and the spec disagree.

### Task
1. Capture `/v3/api-docs` JSON from a running app
2. Compare against the hand-written `api-spec.yml` with `diff`-style tooling
3. Add one undocumented endpoint and re-run the diff
4. Expected observation: the diff flags the undocumented path, proving that
   generated docs drift the moment a handler lacks `@Operation` metadata
