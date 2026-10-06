# Lab 10: API Design & Evolution at Scale — Mini Project

## Project: `ApiLab` — An API That Evolves Without Breaking Anyone

**Time**: 10–14 hours | **Difficulty**: Advanced | **Stack**: Java 21, Spring Boot 3, springdoc-openapi, oasdiff, WireMock (as the "old" client), Testcontainers (Postgres), Pact or Spring Cloud Contract, Redis

Build an order/invoice API, then spend most of your time *evolving* it — adding fields, tightening validation, introducing a deprecated endpoint — while a set of simulated legacy clients keeps running against it. Your goal: reach the end with zero client breakage and a CI gate that prevents it.

---

## Part 1 — v1: the honest starting point

```
[legacy-client (WireMock stubs, fixed expectations)] → [orders-api:8080] → [postgres]
```

Start from a design you would plausibly ship, so it has real flaws to fix:

```java
// v1 — GET /api/v1/orders
@GetMapping("/api/v1/orders")
public List<OrderDto> list(@RequestParam(defaultValue = "0") int page,
                            @RequestParam(defaultValue = "50") int size,
                            @RequestParam(defaultValue = "createdAt") String sort) {
    return repo.findAll(PageRequest.of(page, size, Sort.by(sort))).stream().map(OrderDto::from).toList();
}

// v1 — GET /api/v1/orders/{id}
@GetMapping("/api/v1/orders/{id}")
public Map<String, Object> get(@PathVariable UUID id) {
    Order o = repo.findById(id).orElseThrow(() -> new NotFound("order " + id));
    return Map.of("id", o.getId(), "total", o.getTotal(), "status", o.getStatus(),   // raw Map: no schema
                 "customerEmail", o.getCustomerEmail());                            // PII exposed by default
}

// v1 — POST /api/v1/orders
@PostMapping("/api/v1/orders")
public ResponseEntity<Map<String, Object>> create(@RequestBody Map<String, Object> body) {
    Order o = orders.fromMap(body);          // mass assignment: client controls status and total
    repo.save(o);
    return ResponseEntity.ok(Map.of("ok", true, "orderId", o.getId()));   // 200, no Location, no schema
}
```

**Deliverable**: `V1_POSTMORTEM.md` — enumerate every design flaw you can see now that you have to live with it: no schema, `Map` bodies, unbounded `size`, client-controlled `sort`, PII by default, mass assignment, no idempotency, no error catalogue, offset pagination. This is your "before".

---

## Part 2 — The error catalogue (do this first, retrofit everything else onto it)

```java
public record ProblemDetail(URI type, String title, int status, String detail,
                            String instance, String code, List<FieldError> errors) {

    public record FieldError(String field, String code, String message) {}

    public static final String BASE = "https://errors.example.com/";

    /** type URIs are append-only and documented; the `code` enum is what clients branch on. */
    public static ProblemDetail of(ErrorCode code, String instance, String detail) {
        return new ProblemDetail(URI.create(BASE + code.getSlug()), code.getTitle(),
                                 code.getStatus(), detail, instance, code.name(), List.of());
    }
}

public enum ErrorCode {
    ORDER_NOT_FOUND("order/not-found", "Order not found", 404),
    ORDER_STATE_CONFLICT("order/state-conflict", "Illegal state transition", 409),
    VALIDATION_FAILED("validation/failed", "Validation failed", 422),
    IDEMPOTENCY_MISMATCH("idempotency/mismatch", "Key reused with a different payload", 409),
    RATE_LIMITED("platform/rate-limited", "Too many requests", 429),
    PAGE_SIZE_EXCEEDED("platform/page-size-exceeded", "Requested page size above maximum", 422);

    private final String slug, title; private final int status;
    ErrorCode(String slug, String title, int status) { this.slug = slug; this.title = title; this.status = status; }
    public String getSlug() { return slug; } public String getTitle() { return title; } public int getStatus() { return status; }
}
```

```java
@RestControllerAdvice
class ProblemHandler {

    @ExceptionHandler(OrderNotFoundException.class)
    ResponseEntity<ProblemDetail> notFound(OrderNotFoundException e, HttpServletRequest req) {
        ProblemDetail p = ProblemDetail.of(ErrorCode.ORDER_NOT_FOUND, req.getRequestURI(), e.getMessage());
        return ResponseEntity.status(p.status())
            .contentType(MediaType.APPLICATION_PROBLEM_JSON)
            .body(p);
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    ResponseEntity<ProblemDetail> invalid(MethodArgumentNotValidException e, HttpServletRequest req) {
        var errors = e.getBindingResult().getFieldErrors().stream()
            .map(f -> new ProblemDetail.FieldError(f.getField(), f.getCode(), f.getDefaultMessage())).toList();
        ProblemDetail p = new ProblemDetail(URI.create(ProblemDetail.BASE + "validation/failed"),
            "Validation failed", 422, "One or more fields are invalid", req.getRequestURI(), "VALIDATION_FAILED", errors);
        return ResponseEntity.unprocessableEntity().contentType(MediaType.APPLICATION_PROBLEM_JSON).body(p);
    }
}
```

**Deliverable**: `ERROR_CATALOGUE.md` — every error code, its HTTP status, its `type` URI, and the exact JSON. Plus a test asserting no stack trace, class name, or SQL ever appears in a `detail`.

---

## Part 3 — v2: typed, bounded, safe

### 3.1 Typed contract + generated schema

```java
public record OrderDto(UUID id, UUID customerId, String status, long totalAmountMinor,
                       String currencyCode, Instant createdAt, Instant updatedAt) {}

// PII (`customerEmail`) is REMOVED from the default representation.
```

Generate OpenAPI from the controllers; CI verifies the committed `openapi.yaml` matches the generated one, so the spec cannot drift.

### 3.2 Cursor pagination with a signed opaque token

```java
@Component
class CursorCodec {
    private static final String SECRET = ...;                  // injected, not hardcoded
    private final Mac mac;

    CursorCodec(SecretKey key) throws Exception {
        mac = Mac.getInstance("HmacSHA256");
        mac.init(key);
    }

    record Cursor(int v, String fingerprint, Instant createdAt, UUID id) {}

    String encode(SortKey last, QueryFingerprint fp) {
        String payload = Base64.getUrlEncoder().withoutPadding()
                .encodeToString(canonicalJson(Map.of("v", 1, "fp", fp.value(),
                                                     "createdAt", last.createdAt().toString(), "id", last.id().toString())));
        String sig = Base64.getUrlEncoder().withoutPadding()
                .encodeToString(mac.doFinal(payload.getBytes(UTF_8)));
        return payload + "." + sig;                              // ~80 bytes; signature is the security part
    }

    Cursor decode(String token) {
        var parts = token.split("\\.");
        if (parts.length != 2) throw new BadRequestException("malformed cursor");
        byte[] payload = Base64.getUrlDecoder().decode(parts[0]);
        if (!MessageDigest.isEqual(mac.doFinal(payload), Base64.getUrlDecoder().decode(parts[1])))
            throw new BadRequestException("cursor signature invalid");   // constant-time compare
        return objectMapper.readValue(payload, Cursor.class);
    }
}
```

```java
@GetMapping("/api/v2/orders")
public OrderPage list(@RequestParam(required = false) String after,
                      @RequestParam(defaultValue = "50") @Max(100) int limit,
                      @RequestParam(defaultValue = "createdAt") String sort,
                      OrderQueryFilters filters) {
    if (limit > 100) throw new PageSizeExceededException(limit, 100);
    SortKey last = (after == null) ? null : cursors.decode(after).key();
    List<Order> rows = repo.page(last, limit + 1, sort, filters);          // limit+1 for hasMore
    boolean hasMore = rows.size() > limit;
    List<OrderDto> page = rows.stream().limit(limit).map(OrderDto::from).toList();
    return new OrderPage(page, hasMore ? cursors.encode(SortKey.of(page.getLast()), filters) : null, hasMore);
}
```

Repository query with a deterministic tiebreaker:

```sql
SELECT * FROM orders
WHERE (created_at, id) < (:lastCreatedAt, :lastId)
  AND status = :status
ORDER BY created_at DESC, id DESC
LIMIT :limitPlusOne;
```

**Deliverable**: `PAGINATION.md` — measured query plans and timings for page 1 and page 5,000 under offset vs keyset, showing the keyset plan is constant-time.

### 3.3 Limits everywhere

```java
@PostMapping("/api/v2/orders/bulk")
public BulkResult bulk(@Valid @RequestBody BulkCreateRequest req) {
    if (req.items().size() > 100)                 // hard cap: 100, not 1000
        throw new PageSizeExceededException(req.items().size(), 100);
    List<BulkItemResult> results = new ArrayList<>(req.items().size());
    for (int i = 0; i < req.items().size(); i++) {
        try {
            OrderDto created = createOne(req.items().get(i));
            results.add(new BulkItemResult(i, created.id(), 201, null));
        } catch (DomainException e) {
            results.add(new BulkItemResult(i, null, e.code().getStatus(),
                                            ProblemDetail.of(e.code(), "/api/v2/orders/bulk", e.getMessage())));
        }
    }
    return new BulkResult(results);
}
```

### 3.4 Idempotency

```java
@RestController
class OrderController {

    @PostMapping("/api/v2/orders")
    ResponseEntity<OrderDto> create(@RequestHeader("Idempotency-Key") UUID key,
                                    @Valid @RequestBody CreateOrderRequest body) {
        String requestHash = sha256(canonicalJson(body));
        Optional<StoredResponse> prior = idempotency.find(key);
        if (prior.isPresent()) {
            if (!prior.get().requestHash().equals(requestHash))
                throw new IdempotencyMismatchException(key);   // 409, not a silent replay
            return prior.get().replay();                        // verbatim status + body
        }
        OrderDto created = orders.create(body);
        idempotency.store(key, requestHash, 201, created, Duration.ofHours(24));
        return ResponseEntity.created(URI.create("/api/v2/orders/" + created.id())).body(created);
    }
}
```

With a TTL index and a batched pruner:

```sql
CREATE INDEX ON idempotency_keys (expires_at);
-- scheduled: DELETE FROM idempotency_keys WHERE expires_at < now() ORDER BY expires_at LIMIT 10000;
```

**Deliverable**: a test file proving (a) a replay returns the identical body and status, (b) a reused key with a different payload returns 409, (c) concurrent same-key requests do not create two orders, (d) the record expires after 24 h.

---

## Part 4 — The legacy client (the thing you must not break)

WireMock stubs representing three real clients with **different** expectations:

```java
// Client A: strict Jackson — FAILS on unknown properties
new MappingBuilder()
    .withRequest(new WireMockSchema(pattern).urlPathEqualTo("/api/v2/orders"))
    .willReturn(aResponse().withStatus(200).withHeader("Content-Type", "application/json")
        .withBody(new ObjectMapper().enable(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES)
                    .writeValueAsString(expectedV2Shape))));

// Client B: sealed-type + exhaustive switch on status — breaks on a NEW enum value
// Client C: generated client from the committed openapi.yaml — breaks if the schema changes unexpectedly
```

Every test run executes all three clients against the current server.

**Deliverable**: a test suite where any *unintended* change fails at least one client. Then prove the discipline by making three deliberate changes:

| Change | Verdict | Which client would have broken |
|---|---|---|
| Add optional `updatedAt` to response | safe | none (A tolerates? — verify) |
| Add `PARTIALLY_PAID` enum value | risky | B (exhaustive switch) |
| Make `totalAmountMinor` nullable | **breaking** | A, B, C |

For the third, the correct action is a new required field or a v3 — not a nullable change.

---

## Part 5 — Breaking-change CI gate

```yaml
# .github/workflows/contract.yml
contract:
  steps:
    - uses: actions/checkout@v4
      with: { fetch-depth: 0 }
    - run: ./mvnw -q verify                     # runs provider + consumer contract tests
    - name: Spec is committed and current
      run: |
        ./mvnw -q spring-boot:run & sleep 45     # or use the build plugin
        curl -s localhost:8080/v3/api-docs > /tmp/generated.yaml
        diff -u openapi.yaml /tmp/generated.yaml || (echo "spec drifted"; exit 1)
    - name: Detect breaking changes vs main
      run: |
        git fetch origin main
        curl -s -o base.yaml "https://raw.githubusercontent.com/$REPO/main/openapi.yaml"
        # oasdiff fails the build on breaking changes; --fail-on-ERR is the setting that matters
        oasdiff breaking base.yaml openapi.yaml --fail-on-ERR --format text
    - name: Allow an intentional break with an ADR
      run: |
        if [ -n "$ALLOW_BREAKING" ]; then
          test -f "adr/ADR-${ALLOW_BREAKING}.md" || { echo "breaking change requires an ADR"; exit 1; }
          oasdiff breaking base.yaml openapi.yaml --fail-on-ERR || \
            echo "breaking change approved via ADR ${ALLOW_BREAKING}"
        fi
```

**Acceptance**: a PR making `totalAmountMinor` nullable fails with a specific diff. A PR with `ALLOW_BREAKING=<n>` and a matching ADR passes but leaves a permanent trail. A PR adding an optional field passes silently.

---

## Part 6 — Deprecation workflow (with real usage data)

```java
@Deprecated(since = "2.4", forRemoval = true)
@GetMapping("/api/v1/orders")
public List<OrderDto> legacyList(...) {
    usage.record("GET /api/v1/orders", clientId(request));   // per-client usage — the whole point
    log.warn("Deprecated endpoint used: GET /api/v1/orders by client={}", clientId(request));
    return ...;
}
```

Response headers via a filter:

```java
@Bean
Filter deprecationHeaders() {
    return (req, res, chain) -> {
        if (req.getRequestURI().startsWith("/api/v1/")) {
            res.setHeader("Deprecation", "true");
            res.setHeader("Sunset", "Tue, 01 Jul 2025 00:00:00 GMT");
            res.setHeader("Link", "<https://docs.example.com/api/v2>; rel="successor-version"");
        }
        chain.doFilter(req, res);
    };
}
```

Then compute feasibility:

```
unknown_share = 0.40,  days_remaining = 90
required_daily_migration = 1 - (1 - 0.40)^(1/90) = 0.0057 = 0.57%/day
```

**Deliverable**: `DEPRECATION_PLAN.md` with the measured per-client usage table, the required migration rate, the chosen sunset date (adjusted to the arithmetic), the outreach list, and what happens on the sunset date (410 + `Link` to the successor).

---

## Part 7 — Rate limiting and quota

```java
@Bean
RateLimiter tenantLimiter(RedisRateLimiter limiter) {
    // capacity = 5 × rate: absorb a burst, reject the sustained excess
    return limiter.configure("api").limit(Rate.of(100)).interval(Duration.ofSeconds(1))
                    .initialCapacity(500)
                    .onRejected(() -> tooManyRequests());   // 429 + Retry-After
}
```

Plus a global edge-style backstop at the gateway, sized at `C/3`.

**Deliverable**: a load test showing (a) a compliant client with jitter never sees a 429 under normal load, (b) a single abusive tenant cannot exceed its share and cannot starve others, (c) `Retry-After` is present and a compliant client recovers within seconds.

---

## Acceptance Criteria

- [ ] `V1_POSTMORTEM.md` enumerates the flaws before you fix them.
- [ ] `ERROR_CATALOGUE.md` covers every error with a stable `type` URI; a test proves no stack trace or SQL leaks.
- [ ] Cursor pagination: signed, tamper-evident, constant-cost at page 1 and page 5,000 (with a plan/timing table).
- [ ] `limit`, page size, and batch size are all server-capped and each has a test asserting the cap.
- [ ] Idempotency: verbatim replay, 409 on payload mismatch, no double-create under concurrency, TTL pruning.
- [ ] Three simulated legacy clients run on every build; the three deliberate changes produce the predicted verdicts.
- [ ] CI blocking-change gate catches the nullable change and honours the ADR escape hatch.
- [ ] `DEPRECATION_PLAN.md` has real per-client usage data and a sunset date justified by the migration-rate arithmetic.
- [ ] Rate-limit test proves one abusive tenant cannot starve the fleet.

---

## Stretch

- Generate the client SDK from the spec and run the consumer tests against the generated client instead of WireMock.
- Add `AsyncAPI` for an async event API and an AsyncAPI contract test in the same CI shape.
- Implement `PATCH` with JSON Merge Patch and prove idempotency under retry.
- Add conditional GET (`ETag`/`If-None-Match`) and measure the hit-ratio improvement on the list endpoint.
