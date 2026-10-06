# API Gateways - Flashcards

60 review cards. Front is the prompt; back is the answer.

## Front: What is the rule for what belongs in an API gateway?
**Back:** The gateway answers "can this request proceed?", never "is this request correct?". Anything needing domain knowledge is a service.

## Front: Name the four gateway layers.
**Back:** Edge (TLS/WAF/limits) -> Authentication (verify, don't decode) -> Routing (match, discover, load balance, deadline, limit, break) -> Aggregation (optional BFF).

## Front: What does "verify, not decode" mean?
**Back:** A JWT must have its signature, algorithm, expiry, issuer, and audience checked. Base64-decoding the payload and trusting it is authentication bypass.

## Front: What is the algorithm confusion attack?
**Back:** Attacker sets alg=none, or swaps RS256 for HS256 and signs with the public key as an HMAC secret. Pin the expected algorithm explicitly.

## Front: Why must a gateway strip inbound X-User-Id headers?
**Back:** Otherwise anyone can send X-User-Id: admin with any valid token. Identity headers must be derived from the verified token, never forwarded.

## Front: Why must the gateway's downstream timeout be shorter than the client's?
**Back:** So the gateway can return a useful error and still shape/log the response. Equal timeouts mean the client gave up and discards the gateway's reply.

## Front: Why propagate an absolute deadline rather than a duration?
**Back:** A duration restarts at every hop, so three hops of 950ms allow 2850ms of work. An absolute timestamp is inherited and decremented, bounding the total.

## Front: What does a BFF reduce?
**Back:** Client round-trips and fan-out. It is not a place for business logic, and it introduces a partial-failure surface.

## Front: When is a BFF clearly worth building?
**Back:** Mobile or bandwidth-constrained first-party clients making many round-trips. For browsers with CORS solved, the latency gain rarely justifies it.

## Front: What is partial failure in aggregation?
**Back:** One sub-call fails while others succeed. Each field needs its own criticality flag, timeout, and null fallback.

## Front: When should an aggregated field return 503 rather than null?
**Back:** Only when the field is declared critical. A non-essential service returning 503 takes down the whole page for no reason.

## Front: Why not put a bare null for a failed field?
**Back:** The client cannot distinguish "no data" from "service unavailable". Return null plus a machine-readable error code.

## Front: Why is gateway metrics cardinality dangerous?
**Back:** Labelling with raw paths creates millions of series and can take down the whole metrics backend, killing alerting for every service. Use route templates.

## Front: What is a hop-by-hop header?
**Back:** One meaningful only for a single transport hop (Connection, TE, Transfer-Encoding). Proxies must not forward them. RFC 9110 section 7.6.1.

## Front: Why is route matching by specificity rather than insertion order?
**Back:** /orders/search must beat /orders/{orderId}. Insertion order routes "search" as an id and the request 404s downstream.

## Front: What is path prefix stripping?
**Back:** Removing the matched prefix before forwarding. It must be decided per service and documented; a service assuming the prefix was stripped will 404.

## Front: Why does a gateway need its own circuit breakers?
**Back:** It is the choke point every downstream failure passes through. Without them it queues to a dying service until its own pool is exhausted, turning one service's outage into a platform outage.

## Front: Why is a circuit breaker alone insufficient for capacity protection?
**Back:** A slow-but-not-failing dependency produces no errors, so the breaker never opens and requests pile up. Concurrency limits are also required.

## Front: Why must a gateway not retry non-idempotent requests?
**Back:** A timeout does not tell you the request was not processed. Retrying POST /payments double-charges customers.

## Front: What is retry amplification?
**Back:** client retries x gateway retries x service retries = 18x for 3/2/3. It must be done at exactly one layer, with jitter.

## Front: Why does retrying on timeout specifically cause duplicate charges?
**Back:** The charge may already have succeeded server-side. Retrying sends a second charge for the same logical operation.

## Front: Why is the JWKS cache TTL important?
**Back:** Fetching keys per request adds a network hop and a hard dependency on the identity provider to every request's critical path.

## Front: What breaks with hourly key rotation and a 6-hour JWKS cache?
**Back:** A token with the new kid gets 401 until the next refresh. Every rotation becomes a scheduled authentication outage.

## Front: What is refresh-on-unknown-kid?
**Back:** On an unrecognised kid, do a single-flight rate-limited JWKS refetch while continuing to serve cached keys. This is the essential rotation fix.

## Front: Why single-flight the JWKS refetch?
**Back:** Otherwise 10,000 requests with the new kid cause 10,000 fetches to the identity provider, turning rotation into a self-inflicted DoS.

## Front: How should the gateway derive local rate limits?
**Back:** local = ceil(global / instances) * 1.2. The safety factor stops one instance consuming the whole global budget.

## Front: What happens if the local rate limit is set equal to global/instances?
**Back:** A single noisy instance can spend the entire global budget alone, starving all other tenants.

## Front: On which endpoints should a gateway fail closed when the limiter store is down?
**Back:** Authentication and paid endpoints. A second login attempt costs far less than a credential-stuffing attack succeeding.

## Front: What status code and headers should a rate-limited response carry?
**Back:** 429 with Retry-After, plus RateLimit-Limit, RateLimit-Remaining, and RateLimit-Reset so well-behaved clients can self-throttle.

## Front: Why is a global rate limit useless?
**Back:** It lets one tenant starve all others. Fairness requires per-tenant or per-key limits.

## Front: What is Little's Law applied to gateway concurrency?
**Back:** concurrency = throughput x service_time. With fan-out, multiply by the fan-out factor: 500 rps x 0.08s x 5 = 200 connections per instance.

## Front: Why does a 5-service parallel fan-out have a much worse p99?
**Back:** P(all five under 400ms) = 0.99^5 = 0.951, so the fan-out's p95 is already a single service's p99. Tails compound across parallel work.

## Front: What is the p99 of a parallel fan-out relative to a single service's?
**Back:** Several times worse, roughly the 99.6th percentile of the individual distribution. This is why per-field timeouts are structural.

## Front: Why use copy-on-write for route table reloads?
**Back:** Mutating in place lets concurrent requests see a half-applied config. An AtomicReference swap makes reloads instantaneous and invisible.

## Front: What should the gateway strip before forwarding to a service?
**Back:** Hop-by-hop headers, the raw Authorization header, and every inbound identity or privilege header (X-User-Id, X-Tenant-Id, X-Internal-Call).

## Front: Why not forward the raw JWT to downstream services?
**Back:** It is 600-1200 bytes on every hop. A normalised short identity header derived from the verified token is cheaper and safer.

## Front: What does an edge layer do that auth does not?
**Back:** TLS termination, WAF/DDoS, IP allowlisting, body size and header limits, request ID generation, and trace context initialisation.

## Front: What is service discovery at the gateway and why cache it?
**Back:** Mapping service name to instances. Cached, because a discovery outage must not stop routing when the services themselves are fine. Keep a static fallback table.

## Front: Why does a gateway need a static fallback for discovery?
**Back:** If discovery is unavailable and there is no fallback, routing stops even though every service is healthy. That is a self-inflicted outage.

## Front: What is the availability formula for a gateway?
**Back:** A_gateway = A_network x A_compute x A_config x A_auth_dependency. For 99.99% each dependency must be ~99.997% or better.

## Front: Which gateway dependency is usually weakest?
**Back:** The identity provider via JWKS. Cache it hard with a long TTL and refresh on unknown kid so you do not depend on it per request.

## Front: Should gateway config be pushed or fetched?
**Back:** Pushed. Fetching at runtime makes a config service a hard dependency in the request path.

## Front: How many distinct timeouts should a gateway apply per dependency?
**Back:** At least two: connect timeout and total/read timeout. A single total timeout leaves connections hanging on slow connects.

## Front: What should the gateway do when a breaker is open?
**Back:** Fail fast with a real status and Retry-After, rather than queueing. Queueing is what exhausts the gateway's connections.

## Front: What is the golden-signal breakdown for a gateway?
**Back:** RED metrics (rate, errors, duration) per ROUTE, not aggregated. Plus per-downstream-service latency and error rate for attribution.

## Front: Why is a per-route gateway breakdown essential?
**Back:** A gateway-level p99 hides one broken service entirely. Without the breakdown you cannot attribute a latency spike to a cause.

## Front: What request metadata should the gateway attach for attribution?
**Back:** Request ID, trace context, and the matched route template. Never the raw path as a metric label.

## Front: Should the gateway do authorisation at resource level?
**Back:** No. Route-level scope check at the gateway; resource-level authorisation ("may this user refund this order") stays in the service.

## Front: Why is a mesh preferable to a gateway for internal traffic?
**Back:** Internal callers are semi-trusted and already have network position. A mesh gives mTLS, retries, and telemetry without adding an application-layer hop.

## Front: When is a gateway not worth building?
**Back:** Few services, all internal traffic, or a single first-party client. Then the hop adds a component and latency for little benefit.

## Front: Should a mobile BFF and a partner-facing gateway be the same deployment?
**Back:** No. They have different consumers, latency profiles, and failure modes. Merging them serves neither well.

## Front: What is the biggest reason to strip hop-by-hop headers?
**Back:** They describe a single transport hop and are meaningless (or misleading) forwarded. Connection and Transfer-Encoding in particular can break framing.

## Front: How do you keep a gateway from becoming a monolith?
**Back:** Enforce the "proceed, not correct" rule in code review, and keep gateway source size visible as a metric. Growth is the symptom.

## Front: What is the JWKS rotation vs TTL rule?
**Back:** The cache TTL must EXCEED the rotation interval. TTL shorter than rotation means a guaranteed miss at every rotation.

## Front: What happens if the gateway cannot reach the identity provider during a refresh?
**Back:** Keep serving the cached keys. Do not clear the cache on refresh failure, or an identity provider blip becomes a full authentication outage.

## Front: What is the p95-of-fan-out lesson for timeouts?
**Back:** Set per-field timeouts below your overall client budget, because parallel tails otherwise push the aggregate past what clients tolerate.

## Front: Name three things you check when gateway latency triples at stable CPU.
**Back:** auth-stage latency (JWKS storm), per-downstream-service breakdown (which dependency degraded), and breaker state (half-open probe storm).

## Front: What is the safe default for a gateway that cannot determine a route?
**Back:** 404 with a clear problem-details body. Never fall through to a default route, which turns misconfiguration into wrong-service traffic.

## Front: Why must a gateway validate a pushed route config before propagating it?
**Back:** A bad config breaks every request on the affected route simultaneously. Validate that the change is compatible with existing routes and that every target service exists, then swap atomically.

## Front: What is the failure mode of forwarding a raw JWT to every downstream service?
**Back:** 600-1200 bytes of header on every hop, plus it gives downstream services a signing-verification job they will implement inconsistently. Normalise to a short identity header derived once at the edge.