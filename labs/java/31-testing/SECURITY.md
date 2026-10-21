# Security of Tests

## Test Secrets

Never hardcode credentials, API keys, or certificates in test files. Use:
- Environment variables: System.getenv("TEST_DB_PASSWORD")
- Vault integration: HashiCorp Vault, AWS Secrets Manager
- Mocked security services: No real credentials needed

## Testing Security-Critical Code

### Input Validation
`java
@Test
void sqlInjectionPrevention() {
    String malicious = "' OR '1'='1";
    User result = userService.findByEmail(malicious);
    assertNull(result);  // Should not return data
}
`

### Authentication Tests
`java
@Test
void invalidTokenRejected() {
    assertThrows(AuthenticationException.class,
        () -> authService.authenticate("fake-token"));
}
`

### Authorization Tests
`java
@Test
void userCannotAccessAdminEndpoint() {
    User regularUser = new User("alice", Role.USER);
    assertThrows(AccessDeniedException.class,
        () -> adminService.deleteUser(regularUser, 1L));
}
`

## Secure Test Practices

1. **Don't log secrets**: Test output may be captured in CI logs
2. **Clean up test data**: Delete sensitive test data after tests
3. **Use test containers**: Isolated databases prevent data leaks
4. **Don't test in production**: Use separate test environments
5. **Scan test dependencies**: Dependencies like WireMock or Testcontainers should be up-to-date

## Dependency Security

Test dependencies execute arbitrary code. Verify:
- Use known versions (not SNAPSHOT)
- Run mvn dependency-check or gradle ossIndexAudit
- Only import what you need (avoid test scope pollution)

## SecureRandom in Tests

When testing cryptographic code, mock SecureRandom with a known seed for deterministic tests.
