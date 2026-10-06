# API Gateways - Code Deep Dive

Pure Java. Each section names the production bug it prevents.

## 1. Route Table with Longest-Prefix Matching and Parameters

```java
package systemdesign.apigateway;

import java.util.*;
import java.util.concurrent.atomic.AtomicReference;
import java.util.regex.Pattern;

/**
 * Longest-prefix matching with path parameters, atomically reloadable.
 *
 * TWO BUGS THIS PREVENTS:
 *  1. Iteration-order matching: if `/orders/special` is checked before
 *     `/orders/{orderId}`, "special" gets routed as an order id. Matching must
 *     be by SPECIFICITY, not by registration order.
 *  2. Torn config reload: mutating the table in place means some requests see
 *     a half-applied config. Use copy-on-write plus an AtomicReference swap,
 *     so a reload is invisible and instantaneous.
 */
public final class RouteTable {

    public record Route(String method, Pattern pattern, int literalSegments,
                        String service, boolean stripPrefix, int timeoutMs) {
        public static Route of(String method, String regex, String service,
                               boolean stripPrefix, int timeoutMs) {
            return new Route(method, Pattern.compile(regex), countLiterals(regex),
                             service, stripPrefix, timeoutMs);
        }
        private static int countLiterals(String regex) {
            // Specificity heuristic: fewer wildcards, more literal segments.
            return (int) regex.chars().filter(c -> c == '/').count()
                 - (int) regex.chars().filter(c -> c == '{').count() * 0;
        }
    }

    private final AtomicReference<List<Route>> routes = new AtomicReference<>(List.of());

    /** Copy-on-write: build the new list, then swap. Never mutate in place. */
    public void replaceAll(List<Route> newRoutes) {
        // Sort by descending specificity so the first match is the right match.
        List<Route> sorted = new ArrayList<>(newRoutes);
        sorted.sort(Comparator
                .comparingInt(Route::literalSegments).reversed()
                .thenComparing(r -> r.pattern().pattern().length()).reversed());
        routes.set(List.copyOf(sorted));      // atomic swap; readers see old or new
    }

    public record Match(Route route, java.util.Map<String, String> pathParams,
                        String forwardedPath) {}

    public Optional<Match> match(String method, String path) {
        for (Route r : routes.get()) {
            if (!r.method().equalsIgnoreCase(method)) continue;
            var m = r.pattern().matcher(path);
            if (!m.matches()) continue;

            // Extract {name} parameters positionally.
            Map<String, String> params = new LinkedHashMap<>();
            for (int i = 1; i <= m.groupCount(); i++) {
                String name = paramName(r.pattern().pattern(), i);
                params.put(name, m.group(i));
            }
            String forwarded = r.stripPrefix() ? stripFirstSegment(path) : path;
            return Optional.of(new Match(r, params, forwarded));
        }
        return Optional.empty();
    }

    private static String paramName(String regex, int group) {
        int open = -1, count = 0;
        for (int i = 0; i < regex.length(); i++) {
            if (regex.charAt(i) == '{') { if (++count == group) open = i; }
            else if (regex.charAt(i) == '}' && open >= 0) {
                return regex.substring(open + 1, i);
            }
        }
        return "p" + group;
    }

    private static String stripFirstSegment(String path) {
        int idx = path.indexOf('/', 1);
        return idx < 0 ? "/" : path.substring(idx);
    }
}
```

**Residual risk:** a path like `/orders/{id}/items/../secret` needs
normalisation before matching. Normalise first, match second, and reject `..`
rather than trying to reason about it in the router.

## 2. JWT Verification With a Cached JWKS

```java
/**
 * The gateway must VERIFY, not merely DECODE.
 *
 * A gateway that base64-decodes the JWT and forwards the claims has no
 * authentication at all -- and it is not a subtle bug, because the code looks
 * correct. Verify: signature, algorithm, expiry, issuer, audience.
 *
 * JWKS CACHING is the availability control. Fetching keys per request adds a
 * network hop and a hard dependency on the identity provider to the critical
 * path of every request.
 */
public final class JwtVerifier {

    public record Claims(String subject, String issuer, java.util.List<String> scopes,
                         String tenantId, long expiresAtEpochSeconds) {}

    public final class JwtException extends RuntimeException {
        public JwtException(String m) { super(m); }
    }

    /** kid -> public key. Refreshed lazily on unknown kid (key rotation). */
    private final Map<String, Object> keyCache = new java.util.concurrent.ConcurrentHashMap<>();
    private volatile long keyCacheExpiresAt = 0;
    private static final long JWKS_TTL_MILLIS = 6 * 3600_000L;   // > rotation interval

    private final String expectedIssuer;
    private final String expectedAudience;
    private final java.util.function.Supplier<Map<String, Object>> jwksFetcher;

    public JwtVerifier(String issuer, String audience,
                       java.util.function.Supplier<Map<String, Object>> fetcher) {
        this.expectedIssuer = issuer;
        this.expectedAudience = audience;
        this.jwksFetcher = fetcher;
    }

    private void ensureKeysFresh(String kid) {
        long now = System.currentTimeMillis();
        boolean unknownKid = !keyCache.containsKey(kid);
        if (now >= keyCacheExpiresAt || unknownKid) {
            synchronized (this) {
                if (now >= keyCacheExpiresAt || !keyCache.containsKey(kid)) {
                    keyCache.clear();
                    keyCache.putAll(jwksFetcher.get());     // one fetch, shared
                    keyCacheExpiresAt = now + JWKS_TTL_MILLIS;
                }
            }
        }
    }

    public Claims verify(String jwt) {
        String[] parts = jwt.split("\\.");
        if (parts.length != 3) throw new JwtException("malformed token");

        java.util.Map<String, Object> header = decodeSegment(parts[0]);
        java.util.Map<String, Object> payload = decodeSegment(parts[1]);

        // (1) ALGORITHM CONFUSION: an attacker can set alg=none or swap RS256
        //     for HS256 and sign with the public key as an HMAC secret. Pin the
        //     expected algorithm explicitly; never trust the header's alg.
        String alg = String.valueOf(header.get("alg"));
        if (!"RS256".equals(alg)) throw new JwtException("unexpected alg: " + alg);

        String kid = String.valueOf(header.get("kid"));
        ensureKeysFresh(kid);
        Object key = keyCache.get(kid);
        if (key == null) throw new JwtException("unknown kid (rotation window?)");

        // (2) SIGNATURE
        if (!hmacVerify(parts[0] + "." + parts[1], parts[2], key)) {
            throw new JwtException("bad signature");
        }

        // (3-5) CLAIMS. Missing claim checks are how expired and
        //       wrong-audience tokens get accepted.
        String iss = String.valueOf(payload.get("iss"));
        if (!expectedIssuer.equals(iss)) throw new JwtException("bad issuer");

        Object aud = payload.get("aud");
        boolean audOk = aud instanceof String s ? expectedAudience.equals(s)
                        : aud instanceof java.util.List<?> l ? l.contains(expectedAudience)
                        : false;
        if (!audOk) throw new JwtException("bad audience");

        long exp = ((Number) payload.get("exp")).longValue();
        if (System.currentTimeMillis() / 1000 > exp) throw new JwtException("expired");

        // (6) CLOCK SKEW tolerance. Bounded and small -- a 60 s leeway is
        //     standard, 10 minutes is an invitation.
        return new Claims(String.valueOf(payload.get("sub")), iss,
                scopesOf(payload), String.valueOf(payload.get("tenant")), exp);
    }

    @SuppressWarnings("unchecked")
    private static java.util.List<String> scopesOf(java.util.Map<String, Object> p) {
        Object s = p.get("scope");
        if (s instanceof String str) return Arrays.asList(str.split(" "));
        if (s instanceof java.util.List<?> l) return (java.util.List<String>) l;
        return List.of();
    }

    static java.util.Map<String, Object> decodeSegment(String seg) {
        try {
            String json = new String(java.util.Base64.getUrlDecoder().decode(seg),
                    java.nio.charset.StandardCharsets.UTF_8);
            // NOTE: real deployments must use a hardened JSON parser here.
            java.util.Map<String, Object> m = new java.util.HashMap<>();
            var mm = java.util.regex.Pattern.compile("\"(\\w+)\":(\"([^\"]*)\"|-?\\d+)")
                    .matcher(json);
            while (mm.find()) {
                m.put(mm.group(1), mm.group(3) != null ? mm.group(3) : Long.parseLong(mm.group(2)));
            }
            return m;
        } catch (Exception e) { throw new JwtException("undecodable segment"); }
    }

    private static boolean hmacVerify(String signingInput, String sigB64, Object key) {
        // Placeholder for asymmetric verification against the JWK.
        // Production: build a java.security.PublicKey from the JWK (RSA modulus +
        // exponent) and call Signature.verify with SHA256withRSA.
        return sigB64 != null && !sigB64.isEmpty();
    }
}
```

**Residual risk:** `decodeSegment` here is regex-based for illustration. Use a
real JSON parser — a hand-rolled decoder is a parser-differential vulnerability
waiting to happen.

## 3. Header Sanitisation (the authentication bypass everyone ships)

```java
/**
 * CRITICAL SECURITY CONTROL.
 *
 * If the gateway forwards inbound identity headers, then ANY caller can send
 *   X-User-Id: admin
 *   X-Tenant-Id: victim-corp
 *   X-Internal-Call: true
 * and become whoever they claim to be.
 *
 * The gateway must generate identity headers FROM the verified token, and
 * remove anything inbound that looks like identity.
 */
public final class HeaderSanitiser {

    /** Hop-by-hop headers must not be forwarded (RFC 9110 7.6.1). */
    private static final Set<String> HOP_BY_HOP = Set.of(
            "connection", "keep-alive", "proxy-authenticate",
            "proxy-authorization", "te", "trailer", "transfer-encoding", "upgrade");

    /** Any inbound header that could be mistaken for identity. */
    private static final Set<String> INBOUND_IDENTITY = Set.of(
            "x-user-id", "x-tenant-id", "x-roles", "x-scopes",
            "x-internal-call", "x-service-identity", "x-admin", "x-impersonate");

    public Map<String, String> sanitise(Map<String, String> inbound,
                                        JwtVerifier.Claims claims,
                                        String routeId) {
        Map<String, String> out = new LinkedHashMap<>();
        inbound.forEach((k, v) -> {
            String lk = k.toLowerCase(Locale.ROOT);
            if (HOP_BY_HOP.contains(lk)) return;             // drop
            if (INBOUND_IDENTITY.contains(lk)) return;        // drop ALWAYS
            if (lk.equals("authorization")) return;           // do not forward raw JWT
            out.put(k, v);
        });

        // Re-derive identity from the VERIFIED token. This is the only source
        // of truth for who the caller is.
        out.put("x-user-id", claims.subject());
        out.put("x-tenant-id", claims.tenantId());
        out.put("x-scopes", String.join(" ", claims.scopes()));
        out.put("x-gateway-route", routeId);                  // for attribution
        return out;
    }
}
```

**Residual risk:** services that trust these headers are only as safe as the
gateway. Any path that bypasses the gateway (internal callers, admin tooling,
a service mesh) must not be treated as authenticated by header alone.

## 4. BFF Aggregator with Per-Field Failure Policy

```java
/**
 * Aggregation introduces PARTIAL FAILURE. The design decision is per field:
 * which sub-calls may fail without failing the response?
 *
 * Sequential is the bug: three 400 ms calls is a 1.2 s endpoint even when each
 * call succeeds. Parallel + per-field timeout + null fallback is ~400 ms and
 * degrades gracefully.
 */
public final class BffAggregator {

    public record FieldSpec(String name, boolean critical, int timeoutMs) {}

    public record FieldResult(Object value, String errorCode, long durationMs) {}

    public interface Fetcher {
        <T> java.util.concurrent.CompletableFuture<T> fetch(
                String name, java.time.Duration timeout);
    }

    /**
     * Fan out in parallel with a per-field timeout.
     *
     * critical=true  -> failure fails the whole response
     * critical=false -> failure becomes a null field with an error code, and
     *                    the response is still 200
     */
    public Map<String, FieldResult> aggregate(List<FieldSpec> specs, Fetcher f) {
        Map<String, java.util.concurrent.CompletableFuture<FieldResult>> futures =
                new LinkedHashMap<>();

        for (FieldSpec spec : specs) {
            futures.put(spec.name(), java.util.concurrent.CompletableFuture
                .supplyAsync(() -> {
                    long start = System.currentTimeMillis();
                    try {
                        Object v = f.fetch(spec.name(),
                                java.time.Duration.ofMillis(spec.timeoutMs))
                                   .get(spec.timeoutMs, java.util.concurrent.TimeUnit.MILLISECONDS);
                        return new FieldResult(v, null,
                                System.currentTimeMillis() - start);
                    } catch (Exception e) {
                        // Record WHY. A bare null tells the client nothing and
                        // tells operations nothing.
                        return new FieldResult(null,
                                e instanceof java.util.concurrent.TimeoutException
                                    ? "UPSTREAM_TIMEOUT" : "UPSTREAM_ERROR",
                                System.currentTimeMillis() - start);
                    }
                })
                .orTimeout(spec.timeoutMs(), java.util.concurrent.TimeUnit.MILLISECONDS)
                .exceptionally(t -> new FieldResult(null, "UPSTREAM_ERROR", 0)));
        }

        // Bounded overall deadline: the sum of parallel calls can still exceed
        // the client's patience, so cap the whole aggregation.
        Map<String, FieldResult> results = new LinkedHashMap<>();
        long deadline = java.time.Duration.ofSeconds(2).toMillis();
        for (var e : futures.entrySet()) {
            try {
                results.put(e.getKey(), e.getValue().get(deadline,
                        java.util.concurrent.TimeUnit.MILLISECONDS));
            } catch (Exception ex) {
                results.put(e.getKey(), new FieldResult(null, "AGGREGATION_DEADLINE", 0));
            }
        }
        return results;
    }

    /** Turn results into a status code. Partial data is still a success. */
    public int statusFor(Map<String, FieldResult> results, List<FieldSpec> specs) {
        for (FieldSpec spec : specs) {
            if (!spec.critical()) continue;
            FieldResult r = results.get(spec.name());
            if (r == null || r.value() == null) return 502;   // upstream failed
        }
        return 200;   // non-critical fields may legitimately be null
    }
}
```

**Residual risk:** a dependency that is slow but not failing consumes the
budget. Without per-downstream circuit breakers, a degraded service turns your
BFF into a slow-request generator instead of a fast-partial-response generator.

## 5. Deadline Propagation (Stop Work Nobody Is Waiting For)

```java
/**
 * Without a propagated deadline, a 400 ms client timeout still causes the
 * gateway to wait 3 s on a downstream call, which still causes the service to
 * do 10 s of work. Wasted capacity compounds across hops.
 *
 * Propagate an ABSOLUTE deadline (epoch millis) rather than a timeout duration,
 * because a duration restarts at every hop and never terminates.
 */
public final class DeadlineContext {

    private static final ThreadLocal<Long> DEADLINE = new ThreadLocal<>();
    public static final String HEADER = "x-gateway-deadline";

    /** Set at the edge from the remaining client patience, minus our own budget. */
    public static void start(long clientTimeoutMs, long selfBudgetMs) {
        DEADLINE.set(System.currentTimeMillis() + Math.max(1, clientTimeoutMs - selfBudgetMs));
    }

    /** Recompute for a downstream hop, subtracting this hop's expected cost. */
    public static String propagate(String headerValue, long downstreamReserveMs) {
        long parent = headerValue != null ? Long.parseLong(headerValue)
                                          : DEADLINE.get() + 30_000;
        long child = Math.min(parent - downstreamReserveMs,
                              System.currentTimeMillis() + 2_000);
        return Long.toString(Math.max(child, 1));
    }

    /** Leave budget for shaping and response, so we answer before the client gives up. */
    public static long remainingForWork() {
        Long d = DEADLINE.get();
        if (d == null) return 30_000;
        return Math.max(0, d - System.currentTimeMillis() - 20);   // 20ms to shape
    }
}
```

**Residual risk:** a service that ignores the header and takes longer wastes
capacity. That is why mesh-level deadline propagation exists — the gateway
cannot enforce it alone.