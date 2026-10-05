# REST APIs - REAL WORLD PROJECT

## Project: OpenLedger — a versioned public API for 3,000 partner integrations

A payments and invoicing platform whose API is consumed directly by partner systems that
cannot all be upgraded at once. The work: a stable contract, real deprecation of an old
version, enforced rate limits and quotas, and a client-facing developer experience.

### Architecture

```
  3,000 partner integrations (v1 in prod, v0 legacy at 18% traffic)
        │  API key + HMAC request signing (replay window enforced)
        ▼
  ┌──────────────── API gateway ────────────────┐
  │  TLS termination │ quota per partner        │
  │  request signing │ schema validation        │
  │  deprecation headers │ rate limiting        │
  └──────────────────┬──────────────────────────┘
                     ▼
  ┌──────────── OpenLedger API v1 ─────────────┐
  │  /v1/accounts  /v1/payments  /v1/invoices  │
  │  /v1/payments/{id}/captures  (subresources) │
  │  problem+json everywhere · OpenAPI published│
  └──────────────────┬──────────────────────────┘
                     ▼
          /v0/* compatibility layer ──> internal service
             (adapts, logs usage per partner, reports daily)
```

### Implementation

The compatibility layer is the real work: it lets v0 traffic be measured and migrated
without breaking a single partner:

```java
/**
 * v0 is NOT a proxy. It adapts: field renames, different pagination (offset -> cursor),
 * and different error shapes, while recording which partner used which feature so the
 * team knows exactly what must exist in v1 before v0 can be switched off.
 */
@RestController
@RequestMapping("/v0")
@Deprecated(since = "2025-03-01", forRemoval = true)
class V0CompatibilityController {

    private final V0FeatureUsage usage;   // the migration intelligence

    @GetMapping("/invoices")
    ResponseEntity<?> listInvoices(HttpServletRequest req,
                                  @RequestParam(defaultValue = "0") int page,
                                  @RequestParam(defaultValue = "50") int size) {
        var partner = partnerContext.partner();
        usage.record("v0.invoices.list.offsetPagination");     // what to prioritise in v1
        usage.record("v0.invoices.list.pageSize." + size);

        Page<Invoice> result = invoiceService.list(partner.accountId(), toCursor(page, size));
        if (req.getHeader("Accept") != null && req.getHeader("Accept").contains("application/json"))
            return ResponseEntity.ok(V0Envelope.wrap(result));  // v0 wrapped {data:...,meta:...}
        return ResponseEntity.ok(V0Envelope.wrap(result));       // v0 always wrapped, even on 200
    }
}
```

Request signing, because API keys alone leak value to anyone who can read a log:

```java
@Service
class SignedRequestAuthenticator {
    /**
     * Partner signs the canonical request. Server recomputes and compares in constant time.
     * The timestamp window is the anti-replay control - a captured request is worthless
     * after 5 minutes, so a stolen log line cannot be replayed indefinitely.
     */
    boolean authenticate(String apiKey, Map<String,String> headers, byte[] body) {
        Partner p = partners.requireActive(apiKey);
        String ts = headers.get("X-Timestamp");
        long skew = Math.abs(Instant.now().getEpochSecond() - Long.parseLong(ts));
        if (skew > MAX_CLOCK_SKEW_SECONDS) throw new ApiException(UNAUTHORIZED, "timestamp outside window");

        String nonce = headers.get("X-Nonce");
        if (nonces.seen(p.id(), nonce)) throw new ApiException(UNAUTHORIZED, "nonce replay");
        nonces.remember(p.id(), nonce, Duration.ofSeconds(MAX_CLOCK_SKEW_SECONDS));

        // Sign method, path, sorted query, timestamp, nonce, and a SHA-256 of the body.
        String canonical = String.join("\n", p.id(), req.getMethod(), canonicalPath(req),
                canonicalQuery(req), ts, nonce, sha256Hex(body));
        byte[] expected = hmacSha256(p.signingSecret(), canonical);
        byte[] presented = decodeHex(headers.get("X-Signature"));
        if (!MessageDigest.isEqual(expected, presented)) throw new ApiException(UNAUTHORIZED, "signature mismatch");
        return true;
    }
}
```

Quotas that are fair between a partner sending 10 rps and one sending 10,000:

```java
@Component
class PartnerQuotaFilter extends OncePerRequestFilter {
    @Override protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain) {
        Partner p = partnerContext.partner();
        Quota q = planOf(p.plan());                       // from the partner's contract tier

        // Two distinct controls. A burst bucket smooths short spikes; a sustained counter
        // enforces the monthly contract total. Conflating them produces either throttling
        // that breaks clients or limits nobody actually respects.
        if (!burstBucket(p.id(), q.burstRate()).tryAcquire(1)) {
            return problem(res, TOO_MANY_REQUESTS, "rate limit exceeded",
                    Map.of("Retry-After", "1", "X-RateLimit-Limit", q.sustainedLimit(),
                           "X-RateLimit-Remaining", "0", "X-RateLimit-Reset", resetEpoch(q)));
        }
        monthlyUsage.increment(p.id());
        decorateResponseWithRateLimitHeaders(res, monthlyUsage.remaining(p.id()), q);
        chain.doFilter(req, res);
    }
}
```

Deprecation as a process, not a header:

```java
@Component
class DeprecationInterceptor {
    @Override public ResponseEntity<?> afterCompletion(...) {
        if (requestPath.startsWith("/v0/")) {
            var usage = usageAnalytics.dailyUsageFor(partner, "v0");
            // Per-partner sunset dates, driven by actual usage rather than one global date.
            // A partner at zero v0 traffic for 90 days is migrated automatically.
            headers.add("Deprecation", "true");
            headers.add("Sunset", usage.zeroTrafficSinceDays(90) ? yesterday : partnerSunsetDate(partner).toString());
            headers.add("Link", "<" + docs.migrationGuideUrl() + ">; rel=\"deprecation\"");
        }
    }
}

/** The migration programme, measured weekly. */
class V0MigrationTracker {
    WeeklyReport report() {
        return new WeeklyReport(
            partnersOnV0: usage.partnersUsing("v0"),
            partnersZeroTraffic90d: usage.zeroTrafficSince(Duration.ofDays(90)),
            topV0Endpoints: usage.topEndpoints("v0", limit: 10),   // prioritises v1 work
            v0ErrorRateByPartner: errors.byPartner("v0"),         // partners with failing v0 code
            projectedSunsetDate: usage.projectedAllMigrated());    // a real date, not a guess
    }
}
```

### Non-functional requirements

- **Availability**: 99.95% for v1; v1 traffic must not be affected by v0 load.
- **Latency**: p95 under 120 ms at the edge, p99 under 400 ms; signing verification is the
  only added CPU cost and is measured.
- **Compatibility**: zero downtime for v0 partners; a partner migration is a config change,
  not a coordinated release.
- **Contract stability**: additive changes only within v1. A breaking change requires v2 with
  a migration guide, published before implementation.
- **Rate limits**: burst plus sustained per plan, with `RateLimit-*` headers on every
  response so clients can self-manage instead of discovering limits by being throttled.
- **Security**: HMAC request signing with a nonce and clock-skew window; API keys are
  identifiers, never the secret; secrets rotatable with a dual-key overlap period.
- **Observability**: per-partner usage of every endpoint, error rate, and latency — the raw
  material for both capacity planning and the v0 migration programme.
- **Deprecation**: per-partner sunset dates; automatic migration only after 90 days of zero
  traffic; a published migration guide and a support path.
- **DX**: OpenAPI spec, a sandbox environment with fake data, and runnable examples in four
  languages — the three things that actually reduce support load.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- RFC 9457 defines the `application/problem+json` error format used for every error
  response, giving clients one machine-readable shape to handle.
  https://www.rfc-editor.org/info/rfc9457/
- MDN HTTP conditional requests documents the `ETag`/`If-Match` optimistic-concurrency
  pattern implemented for PATCH on resources.
  https://developer.mozilla.org/en-US/docs/Web/HTTP/Conditional_requests

## Deliverables

- [x] v1 REST contract: resource design, correct status codes, problem+json everywhere
- [x] v0 compatibility layer that adapts shape, paginates differently, and records usage
- [x] HMAC request signing with nonce replay protection and a clock-skew window
- [x] Burst plus sustained quota enforcement with `RateLimit-*` response headers
- [x] Per-partner deprecation and sunset dates driven by actual usage
- [x] Weekly migration report: remaining partners, top endpoints, projected sunset
- [x] OpenAPI spec, sandbox environment, and runnable multi-language examples
- [x] Additive-change-only policy documented with the v2 migration path
