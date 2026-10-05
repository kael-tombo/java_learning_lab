# API Security Testing - MINI PROJECT

## Project: BreachHunt — test your own API until it breaks, then keep the tests

Build a deliberately vulnerable Spring Boot API, write security tests that find each
vulnerability, fix them, and commit the tests as regression guards. Also assemble a local
SAST + DAST + dependency-scan pipeline.

### Architecture

```
  VULNERABLE API                    TEST LAYERS                        FIX
  ────────────────                  ──────────                         ───
  GET /api/orders/{id}  ──▶ BOLA test: 2 users, 4 orders  ──▶ owner check in service
  POST /api/orders      ──▶ mass assignment: {"role":"ADMIN"}  ──▶ DTO allow-list
  GET  /api/search      ──▶ injection: q=' OR 1=1--           ──▶ parameterised query
  PUT  /api/orders/{id} ──▶ no ETag/If-Match  ──▶ lost update  ──▶ optimistic locking
  (no rate limit)      ──▶ burst test: 1000 req  ──▶ token bucket
  (verbose errors)     ──▶ stack trace in body  ──▶ generic handler
```

### Implementation

The BOLA/IDOR test, which is the highest-value API security test there is:

```java
class BolaRegressionTest {
    // Two real users with their own data. The test asserts user A can never read user B's order,
    // for EVERY order in the system - not just a hand-picked one.
    @Test
    void userCannotReadAnotherUsersOrder() {
        String tokenA = login("alice@example.com");
        String tokenB = login("bob@example.com");
        List<String> bobOrders = ordersOf(tokenB);

        for (String orderId : bobOrders) {
            mockMvc.perform(get("/api/orders/" + orderId).header(AUTHORIZATION, "Bearer " + tokenA))
                   .andExpect(status().isForbidden());   // NOT 404-less 200
        }
    }

    // Also assert the enumeration fix: an order that does not exist at all should not be
    // distinguishable by timing/status from one the user does not own, beyond the minimum.
    @Test
    void nonExistentAndNotOwnedAreIndistinguishable() {
        long t1 = time(() -> get("/api/orders/does-not-exist", tokenA));
        long t2 = time(() -> get("/api/orders/" + bobOrderId, tokenA));
        assertThat(Math.abs(t1 - t2)).isLessThan(50);   // ms; tune to the environment
    }
}
```

Mass assignment and the fix, both versions shown:

```java
// VULNERABLE: binding straight to the domain object lets the client set server-owned fields.
record OrderRequest(String sku, int quantity, String customerId, String role, BigDecimal price) {}
@PostMapping("/orders") Order create(@RequestBody OrderRequest r) { return service.create(r); }

// FIXED: an explicit DTO exposes only what the client may set; enrichment happens server-side.
record CreateOrderCommand(String sku, int quantity) {}      // nothing else is bindable
@PostMapping("/orders")
Order create(@AuthenticationPrincipal JwtUser caller, @Valid @RequestBody CreateOrderCommand cmd) {
    return service.create(cmd.sku(), cmd.quantity(), caller.customerId());  // customerId from the TOKEN
}
```

The injection test, including a note on why the negative test matters:

```java
@Test void searchIsParameterised() {
    mockMvc.perform(get("/api/search").param("q", "' OR '1'='1"))
           .andExpect(status().isOk())
           .andExpect(jsonPath("$.length()").value(0));      // treated as a literal string, not SQL
}

@Test void searchRejectsCommentTerminatedUnion() {
    mockMvc.perform(get("/api/search").param("q", "x'; DROP TABLE orders;--"))
           .andExpect(status().isOk())
           .andExpect(jsonPath("$.length()").value(0));
}

// And the fix, which is a parameterised query - not escaping, not a blacklist.
@Query("SELECT o FROM Order o WHERE LOWER(o.sku) LIKE LOWER(CONCAT('%', :q, '%'))")
List<Order> search(@Param("q") String q);
```

Rate limiting and a test that asserts it, because "there is a limit" is not a test:

```java
@Test void burstIsRateLimited() {
    for (int i = 0; i < 100; i++)
        mockMvc.perform(get("/api/search").param("q", "widget"))
               .andExpect(status().is2xxSuccessful());
    mockMvc.perform(get("/api/search").param("q", "widget"))
           .andExpect(status().isTooManyRequests())
           .andExpect(header().string("Retry-After", exists()));
}
```

Error handling, verified so stack traces cannot leak:

```java
@RestControllerAdvice
class SafeErrorHandler {
    @ExceptionHandler(Exception.class)
    ProblemDetail handle(Exception ex, HttpServletRequest req) {
        String ref = errorRef.record(ex);   // correlation id, full detail in the log only
        return ProblemDetail.forStatusAndDetail(INTERNAL_SERVER_ERROR,
                "An unexpected error occurred. Reference: " + ref);
    }
}

@Test void errorResponseLeaksNothing() throws Exception {
    String body = mockMvc.perform(get("/api/orders/%00")).andReturn().getResponse().getContentAsString();
    assertThat(body).doesNotContain("org.springframework").doesNotContain("Exception")
                    .doesNotContain("SQLException").doesNotContain("jdbc");
}
```

### Deliverables

- [ ] Vulnerable baseline with the BOLA, mass-assignment, and injection tests failing first
- [ ] BOLA test using two real identities across every owned resource
- [ ] Mass-assignment fix using an explicit request DTO (no server-owned field is bindable)
- [ ] Parameterised queries with positive and negative injection tests
- [ ] Rate limiting test asserting 429 and `Retry-After`
- [ ] Error handler test asserting no stack trace, framework, or SQL text in responses
- [ ] Optimistic-locking test for concurrent update (lost update)
- [ ] Pipeline running SAST, dependency scan, and an authenticated DAST scan
- [ ] A `SECURITY_TEST_COVERAGE.md` listing what the pipeline does *not* test
