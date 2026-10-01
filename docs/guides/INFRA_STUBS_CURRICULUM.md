# Infra Stubs Curriculum — Pedagogical Upgrade Path

> Audit date: 2026-10-01. Scope: 41 modules (23–59 + 02-spring-ecosystem + java-master-lab + quarkus-learning/quarkus-getting-started).
> Method: file counts (incl. nested submodules), pom parent check, `mvn -f <module>/pom.xml validate -B`, top-level README/THEORY/QUIZ/EXERCISES (+ PROJECTS.md / PEDAGOGIC_GUIDE.md / SOLUTION notes).
> No code was edited for this audit.

Effort scale: **S** = <0.5 day (docs-only or single-file fix) · **M** = 1–2 days (code + tests + docs) · **L** = 3–5 days (docker/infra, multi-service mini-project, or new framework setup).
Priority: **P0** foundations → **P1** testing/quality → **P2** messaging/data APIs → **P3** cloud-native runtimes → **P4** observability/security/specialty + meta.

## 1. Audit summary (per-module table)

| Module | src-main .java (all nested) | src-test .java | pom inherits java-learning-parent | `mvn validate -B` | README | THEORY | QUIZ | EXERCISES | Notes |
|---|---|---|---|---|---|---|---|---|---|
| 02-spring-ecosystem | 3 | 0 | YES | PASS | YES (14.8KB) | YES (14.1KB) | YES (5.3KB) | YES (18.4KB) | Most complete. 3 submods (batch, cloud-config, cloud-gateway). Missing CODE_DEEP_DIVE/MINI_PROJECT. Boot plugin version warning. |
| 23-observability | 2 | 0 | YES | PASS* | YES (1.5KB thin) | NO | NO | NO | Submods: micrometer-learning, opentelemetry-learning (Lab.java ~5.5KB each). PROJECTS.md 29KB. |
| 24-graalvm-native | 1 | 0 | YES | PASS* | YES (1.4KB thin) | NO | NO | NO | 1 submod, Lab 6.1KB. PROJECTS.md 5KB. |
| 25-kotlin-coroutines | 1 | 0 | YES | PASS | YES (1.2KB) | NO | NO | NO | 1 submod, Lab 2.5KB. PROJECTS.md 18KB. |
| 26-architecture | 1 | 0 | YES | PASS* | YES (1.4KB) | NO | NO | NO | hexagonal-architecture Lab 5KB. PROJECTS.md 30KB. |
| 27-kafka-streams | 1 | 0 | YES | PASS* | YES (1.3KB) | NO | NO | NO | kafka-streams-learning App 341B (hollow stub). PROJECTS.md 24KB. |
| 28-graphql | 1 | 0 | YES | PASS* | YES (1.1KB) | NO | NO | NO | graphql-learning Lab 674B (hollow). PROJECTS.md 19KB. |
| 29-grpc | 1 | 0 | YES | PASS* | YES (1.3KB) | NO | NO | NO | grpc-learning App 316B (hollow). PROJECTS.md 28KB. |
| 30-event-sourcing | 1 | 0 | YES | PASS* | YES (1.3KB) | NO | NO | NO | Lab 2.4KB. PROJECTS.md 26KB. |
| 31-mongodb | 1 | 0 | YES | PASS* | YES (0.9KB) | NO | NO | YES (1.5KB thin) | +PEDAGOGIC_GUIDE.md, PROJECTS.md 9KB. Lab 5.3KB. |
| 32-redis | 1 | 0 | YES | PASS* | YES (1.0KB) | NO | NO | YES (1.4KB thin) | +PEDAGOGIC_GUIDE.md, PROJECTS.md 8KB. Lab 5.3KB. |
| 33-postgresql | 2 | 1 | YES | PASS* | YES (1.0KB) | NO | NO | YES (2.6KB) | Richest stub: top src/ Lab 5.5KB + ExampleTest 7.3KB + nested Lab 6.1KB + SOLUTION/ + DEBUGGING/QUICK_REFERENCE. |
| 34-rabbitmq | 2 | 0 | YES | PASS* | YES (1.0KB) | NO | NO | YES (2.5KB) | Top Lab 5KB + nested Lab 7KB + SOLUTION/. PROJECTS.md 49KB. |
| 35-consul | 2 | 0 | YES | PASS* | YES (1.1KB) | NO | NO | YES (3.2KB) | Top Lab 4.4KB + nested 5.5KB + SOLUTION/. |
| 36-elasticsearch | 2 | 0 | YES | PASS* | YES (1.1KB) | NO | NO | YES (2.3KB) | Top Lab 4.4KB + nested 7.5KB + SOLUTION/. |
| 37-keycloak | 2 | 0 | YES | PASS* | YES (1.0KB) | NO | NO | YES (1.4KB thin) | Top Lab 4KB + nested 6.3KB + SOLUTION/. |
| 38-prometheus | 2 | 0 | YES | PASS* | YES (1.1KB) | NO | NO | YES (1.3KB thin) | Top Lab 3.4KB + nested 8KB + SOLUTION/. |
| 39-grafana | 2 | 0 | YES | PASS* | YES (1.1KB) | NO | NO | YES (1.3KB thin) | Top Lab 4.4KB + nested 6.6KB + SOLUTION/. |
| 40-jaeger | 2 | 0 | YES | PASS* | YES (1.2KB) | NO | NO | YES (1.3KB thin) | Top Lab 4.5KB + nested 7.2KB + SOLUTION/. |
| 41-actuator | 2 | 0 | YES | PASS* | YES (1.3KB) | NO | NO | YES (1.4KB thin) | Top Lab 3.8KB + nested 6.8KB + SOLUTION/. |
| 42-testcontainers | 2 | 0 | YES | PASS | YES (1.2KB) | NO | NO | YES (1.3KB thin) | Top Lab 4.6KB + nested 5.9KB + SOLUTION/. |
| 43-wiremock | 2 | 0 | YES | PASS* | YES (1.1KB) | NO | NO | YES (1.2KB thin) | Top Lab 4.8KB + nested 7.3KB + SOLUTION/. |
| 44-jmeter | 2 | 0 | YES | PASS* | YES (1.0KB) | NO | NO | YES (1.3KB thin) | Top Lab 6KB + nested 8KB + SOLUTION/. |
| 45-gatling | 2 | 0 | YES | PASS* | YES (0.9KB) | NO | NO | YES (1.3KB thin) | Top Lab 6.2KB + nested 9.2KB + SOLUTION/. |
| 46-flyway | 2 | 0 | YES | PASS* | YES (0.7KB thin) | NO | NO | YES (0.7KB stub, 18 lines) | Top Lab 5KB + nested 7KB + SOLUTION/. |
| 47-liquibase | 2 | 0 | YES | PASS* | YES (0.8KB thin) | NO | NO | YES (0.5KB stub, 16 lines) | Top Lab 6KB + nested 8.9KB + SOLUTION/. |
| 48-cucumber | 2 | 0 | YES | PASS | YES (0.7KB thin) | NO | NO | YES (0.5KB stub) | Top Lab 6.7KB + nested CucumberLab 1.3KB + SOLUTION/. PROJECTS.md 5.6KB. |
| 49-selenide | 2 | 0 | YES | PASS | YES (0.7KB thin) | NO | NO | YES (0.5KB stub) | Top Lab 6.9KB + nested 1.3KB + SOLUTION/. PROJECTS.md 3.8KB. |
| 50-junit5 | 2 | 0 | YES | PASS | YES (0.7KB thin) | NO | NO | YES (0.5KB stub) | Top Lab 6.7KB + nested 1.7KB + SOLUTION/. |
| 51-quarkus | 2 | 0 | YES | PASS | YES (0.8KB thin) | NO | NO | YES (0.5KB stub) | Top Lab 2.2KB + nested 1.5KB + SOLUTION/. |
| 52-micronaut | 2 | 0 | YES | PASS* | YES (0.8KB thin) | NO | NO | YES (0.5KB stub) | Top Lab 1.9KB + nested 1.1KB + SOLUTION/. PROJECTS.md 3.1KB. |
| 53-helidon | 2 | 0 | YES | PASS* | YES (0.7KB thin) | NO | NO | YES (0.5KB stub) | Top Lab 1.8KB + nested 1.1KB + SOLUTION/. PROJECTS.md 2.6KB. |
| 54-vertx | 2 | 0 | YES | PASS | YES (0.7KB thin) | NO | NO | YES (0.4KB stub) | Top Lab 2KB + nested 1.2KB + SOLUTION/. |
| 55-kafka | 2 | 0 | YES | PASS | YES (0.7KB thin) | NO | NO | YES (0.5KB stub) | Top Lab 1.9KB + nested 1.5KB + SOLUTION/. |
| 56-k8s | 2 | 0 | YES | PASS* | YES (0.7KB thin) | NO | NO | YES (0.5KB stub) | Top Lab 1.9KB + nested 1.4KB + SOLUTION/. PROJECTS.md 20KB. |
| 57-service-mesh | 2 | 0 | YES | PASS* | YES (0.7KB thin) | NO | NO | YES (0.5KB stub) | Top Lab 2KB + nested 1.2KB + SOLUTION/ 8.7KB + Test. PROJECTS.md 22KB. |
| 58-serverless | 2 | 0 | YES | PASS* | YES (0.7KB thin) | NO | NO | YES (0.5KB stub) | Top Lab 1.9KB + nested 1.3KB + SOLUTION/. PROJECTS.md 33KB. |
| 59-webassembly | 2 | 0 | YES | PASS* | YES (0.7KB thin) | NO | NO | YES (0.4KB stub) | Top Lab 1.9KB + nested 1.3KB + SOLUTION/ 4.5KB. PROJECTS.md 23KB. |
| java-master-lab | 0 | 0 | NO (standalone) | PASS | YES (11KB) | NO | NO | NO | 112 docs/ + labs/ + templates/. Doc-heavy, zero src/main java. Meta-lab, not a thin stub. |
| quarkus-learning/quarkus-getting-started | 1 | 2 | NO (quarkus BOM) | PASS | YES (1.8KB) | NO | NO | NO | Real scaffold: GreetingResource + 2 tests + mvnw. Only reference impl. |

\* PASS with `[WARNING] build.plugins.plugin.version for spring-boot-maven-plugin is missing` in the nested submodule effective model. Harmless for `validate` but should be pinned via parent `pluginManagement` (S fix, do once).

Global gaps: **no module has THEORY.md + QUIZ.md + CODE_DEEP_DIVE.md + MINI_PROJECT.md together** except 02 (has THEORY+QUIZ, lacks DEEP_DIVE+MINI_PROJECT). Zero `src/test` coverage except 33-postgresql and quarkus-getting-started. EXERCISES.md in 46–59 are 16-line stubs. SOLUTION/ dirs exist in 33–59 but are not wired to Maven (no asserts run in CI).

## 2. Priority-ordered upgrade backlog

| Prio | Module | Why this order | Missing pieces → effort |
|---|---|---|---|
| P0-1 | 33-postgresql | Closest to done; DB foundation for flyway/liquibase/jpa | THEORY M · DEEP_DIVE S · EXERCISES S (expand Testcontainers) · QUIZ S · MINI_PROJECT M (CRUD + migrations) |
| P0-2 | 32-redis | Cache foundation; tiny code, high interview value | THEORY S · DEEP_DIVE S · EXERCISES M (TTL, eviction, pub/sub) · QUIZ S · MINI_PROJECT M (cache-aside leaderboard) |
| P0-3 | 31-mongodb | Document-model contrast to postgres/redis | THEORY S · DEEP_DIVE S · EXERCISES M (aggregations, indexes) · QUIZ S · MINI_PROJECT M (catalog + search) |
| P0-4 | 55-kafka | Messaging backbone for streams/event-sourcing | THEORY M · DEEP_DIVE M · EXERCISES M (producer/consumer, idempotency) · QUIZ S · MINI_PROJECT L (orders pipeline w/ docker-compose) |
| P0-5 | 50-junit5 | Test literacy unlocks every other module | THEORY S · DEEP_DIVE M (lifecycle, params, extensions) · EXERCISES M · QUIZ S · MINI_PROJECT S (kata suite) |
| P0-6 | 41-actuator | Cheapest observability win; feeds prometheus/grafana | THEORY S · DEEP_DIVE S · EXERCISES S · QUIZ S · MINI_PROJECT S (health/info/metrics demo) |
| P0-7 | 46-flyway | Pairs with 33; versioned migrations are P0 skill | THEORY S · DEEP_DIVE S · EXERCISES M (baseline, repair, callbacks) · QUIZ S · MINI_PROJECT S (migrate sample schema) |
| P1-1 | 42-testcontainers | Makes 31/32/33/46/47 tests real | THEORY M · DEEP_DIVE M · EXERCISES M · QUIZ S · MINI_PROJECT M (one reusable TC harness) |
| P1-2 | 47-liquibase | Flyway counterpart (XML/YAML/JSON changelogs) | THEORY S · DEEP_DIVE M · EXERCISES M · QUIZ S · MINI_PROJECT S |
| P1-3 | 48-cucumber | BDD layer on top of junit5 | THEORY S · DEEP_DIVE M · EXERCISES M (feature files + glue) · QUIZ S · MINI_PROJECT M (checkout flow) |
| P1-4 | 43-wiremock | Contract/stub testing; cheap, high value | THEORY S · DEEP_DIVE S · EXERCISES M · QUIZ S · MINI_PROJECT S |
| P1-5 | 49-selenide | UI testing; needs isolated profile (no global driver) | THEORY M · DEEP_DIVE M · EXERCISES M · QUIZ S · MINI_PROJECT M (2-page flow, headless) |
| P1-6 | 44-jmeter | Perf baseline; keep non-blocking (no GUI in CI) | THEORY M · DEEP_DIVE M (jmx + thresholds) · EXERCISES M · QUIZ S · MINI_PROJECT M (baseline report) |
| P1-7 | 45-gatling | Code-as-test perf; pair with jmeter, pick one depth | THEORY M · DEEP_DIVE M · EXERCISES M · QUIZ S · MINI_PROJECT M |
| P2-1 | 34-rabbitmq | Classic broker; contrast with kafka | THEORY M · DEEP_DIVE M · EXERCISES M (exchanges, DLQ, ack) · QUIZ S · MINI_PROJECT M (work-queue + DLQ) |
| P2-2 | 27-kafka-streams | Hollow stub (341B); needs real topology | THEORY M · DEEP_DIVE L · EXERCISES L · QUIZ M · MINI_PROJECT L (word-count → windowed agg) |
| P2-3 | 30-event-sourcing | Concept-heavy; build on 55 | THEORY L · DEEP_DIVE M · EXERCISES M (event store, replay) · QUIZ M · MINI_PROJECT L (bank-ledger) |
| P2-4 | 28-graphql | Hollow stub (674B); schema-first needed | THEORY M · DEEP_DIVE M · EXERCISES M (schema, resolvers, N+1) · QUIZ S · MINI_PROJECT M (books API + tests) |
| P2-5 | 29-grpc | Hollow stub (316B); proto toolchain needed | THEORY M · DEEP_DIVE L (proto, codegen, streaming) · EXERCISES M · QUIZ S · MINI_PROJECT M (greeter → CRUD stream) |
| P2-6 | 36-elasticsearch | Mapping/analysis depth; docker-heavy | THEORY M · DEEP_DIVE M · EXERCISES M · QUIZ S · MINI_PROJECT M (index + search relevance) |
| P3-1 | 02-spring-ecosystem | Already richest; close the last mile | CODE_DEEP_DIVE M · MINI_PROJECT M (config-server + gateway + batch job) · tests M (add 1 SmokeTest/submod) |
| P3-2 | 51-quarkus | Panache thin (1.5KB); Quarkus hype justifies early P3 | THEORY M · DEEP_DIVE M · EXERCISES M · QUIZ S · MINI_PROJECT M (REST + Panache + DevSvcs) |
| P3-3 | 52-micronaut | Same shape as 51; keep symmetrical, small | THEORY S · DEEP_DIVE S · EXERCISES M · QUIZ S · MINI_PROJECT S |
| P3-4 | 53-helidon | Same shape; keep symmetrical, small | THEORY S · DEEP_DIVE S · EXERCISES M · QUIZ S · MINI_PROJECT S |
| P3-5 | 54-vertx | Reactive contrast; needs event-loop deep-dive | THEORY M · DEEP_DIVE M · EXERCISES M · QUIZ S · MINI_PROJECT M (web-client fan-out) |
| P3-6 | quarkus-getting-started | Reference impl only; add pedagogy wrapper, don't fork | THEORY S · EXERCISES S (guided tour of existing code) · QUIZ S · MINI_PROJECT S (extend GreetingResource) |
| P3-7 | 56-k8s | Manifests exist in PROJECTS.md; extract to yaml + kind | THEORY M · DEEP_DIVE M · EXERCISES M · QUIZ S · MINI_PROJECT L (deploy + probe + HPA) |
| P3-8 | 57-service-mesh | Istio needs k8s first; demo, not mastery | THEORY M · DEEP_DIVE S · EXERCISES S (traffic split yaml) · QUIZ S · MINI_PROJECT M (canary demo spec) |
| P3-9 | 58-serverless | Functions-framework thin; cold-start story | THEORY S · DEEP_DIVE S · EXERCISES S · QUIZ S · MINI_PROJECT S (http fn + event fn) |
| P4-1 | 23-observability | Umbrella; land after prometheus/grafana/jaeger | THEORY M · DEEP_DIVE M (OTel vs Micrometer) · EXERCISES M · QUIZ S · MINI_PROJECT M (instrument one app E2E) |
| P4-2 | 38-prometheus | Metrics exposition; needs running app | THEORY M · DEEP_DIVE S · EXERCISES M (PromQL basics) · QUIZ S · MINI_PROJECT S (scrape + alert rule) |
| P4-3 | 39-grafana | Dashboard-as-code; pair with 38 | THEORY S · DEEP_DIVE S · EXERCISES S (provisioned dashboard JSON) · QUIZ S · MINI_PROJECT S |
| P4-4 | 40-jaeger | Tracing; pair with OTel in 23 | THEORY S · DEEP_DIVE S · EXERCISES M (trace a 2-hop call) · QUIZ S · MINI_PROJECT S |
| P4-5 | 35-consul | Service discovery; niche vs k8s DNS | THEORY S · DEEP_DIVE S · EXERCISES M · QUIZ S · MINI_PROJECT S (register + health check) |
| P4-6 | 37-keycloak | OIDC depth; docker-heavy, keep scoped | THEORY M · DEEP_DIVE M · EXERCISES M · QUIZ S · MINI_PROJECT M (protect one endpoint, 1 realm JSON) |
| P4-7 | 26-architecture | Hexagonal Lab 5KB exists; needs decision records | THEORY M · DEEP_DIVE M (ports/adapters map) · EXERCISES M (refactor kata) · QUIZ M · MINI_PROJECT M (slice + ADR) |
| P4-8 | 24-graalvm-native | Native-image is L; keep as spike + docs | THEORY M · DEEP_DIVE M · EXERCISES S (reflect-config only) · QUIZ S · MINI_PROJECT L (deferred) |
| P4-9 | 25-kotlin-coroutines | Only non-Java track; interop story | THEORY M · DEEP_DIVE M · EXERCISES M · QUIZ S · MINI_PROJECT M (suspend + Flow demo) |
| P4-10 | 59-webassembly | Most speculative; curiosity track | THEORY S · DEEP_DIVE S · EXERCISES S · QUIZ S · MINI_PROJECT S (WASI hello + notes) |
| P4-11 | java-master-lab | Meta: dedupe 112 docs into index, not new content | THEORY — (write MASTER_INDEX diff) S · EXERCISES — · QUIZ — · MINI_PROJECT — (capstone pointer). Effort M to prune/dupe-link. |

## 3. Per-module upgrade cards

Format: **Needs** = concrete artifacts to add. **Acceptance** = how to verify. **Est** per artifact.

### 02-spring-ecosystem — closest to complete
- THEORY: already exists; add 1 section each for Batch chunk-model, Config refresh, Gateway predicates. Est S.
- CODE_DEEP_DIVE: new file; trace one request through gateway → config → batch job with 3 sequence diagrams. Est M.
- EXERCISES: exists; add 3 runnable tasks (add gateway filter, rotate config prop, add batch step) with `src/test` asserts. Est M.
- QUIZ: exists; add 5 gateway-predicate + 5 batch-restart questions. Est S.
- MINI_PROJECT: `capstone/` or PROJECTS.md pick 1: config-server + gateway + nightly batch with docker-compose. Est M.
- CODE: add 1 `@SpringBootTest` context-load per submod (currently 0 tests). Est S.

### 23-observability
- THEORY (M): pillars (metrics/logs/traces), OTel vs Micrometer, cardinality dangers.
- CODE_DEEP_DIVE (M): annotate both Lab.java files line-by-line; explain exporter config.
- EXERCISES (M): 3 tasks — add a counter, add a span attribute, wire OTLP endpoint via Testcontainers/Docker.
- QUIZ (S): 10 Q (sampling, exemplars, label naming).
- MINI_PROJECT (M): instrument the 41-actuator demo and view in 38/39/40.

### 24-graalvm-native
- THEORY (M): closed-world, reflection config, build-time init.
- CODE_DEEP_DIVE (M): walk Lab.java + required `reflect-config.json`/`resource-config.json` samples.
- EXERCISES (S): `native-image` dry-run profile + 1 reflection fix kata. Mark L work as deferred.
- QUIZ (S): 8 Q.
- MINI_PROJECT (L, deferred): actual `mvn -Pnative` build on CI with size/startup table.

### 25-kotlin-coroutines
- THEORY (M): suspend, dispatchers, structured concurrency, Flow vs Stream.
- CODE_DEEP_DIVE (M): rewrite KotlinCoroutinesLab in idiomatic Kotlin (currently Java file) + interop notes.
- EXERCISES (M): 4 katas (async/await, cancellation, Flow map/filter, test with runTest).
- QUIZ (S): 10 Q.
- MINI_PROJECT (M): CLI that fetches 3 URLs concurrently with timeout + retry.

### 26-architecture
- THEORY (M): hexagonal/ports-adapters, DIP, package fitness functions.
- CODE_DEEP_DIVE (M): map HexagonalLab to ports/adapters; add package diagram.
- EXERCISES (M): refactor anemic service into port + adapter with tests.
- QUIZ (M): 12 Q incl. 2 scenario DQs.
- MINI_PROJECT (M): slice 1 feature + 1 ADR markdown.

### 27-kafka-streams — hollow stub priority
- THEORY (M): KStream/KTable, state stores, exactly-once.
- CODE_DEEP_DIVE (L): replace 341B App with word-count → windowed count, line-by-line.
- EXERCISES (L): 3 topologies with TopologyTestDriver asserts (currently 0 tests).
- QUIZ (M): 10 Q.
- MINI_PROJECT (L): обогащённый join + docker-compose Kafka.

### 28-graphql — hollow stub priority
- THEORY (M): schema-first, resolvers, N+1, pagination (connections).
- CODE_DEEP_DIVE (M): expand 674B Lab into schema + 2 resolvers + DataLoader note.
- EXERCISES (M): add field, add mutation with validation, add integration test.
- QUIZ (S): 8 Q.
- MINI_PROJECT (M): books API + GraphiQL screenshot + tests.

### 29-grpc — hollow stub priority
- THEORY (M): proto3, unary vs streaming, deadlines, interceptors.
- CODE_DEEP_DIVE (L): add `.proto`, maven codegen block, regenerate stub walkthrough.
- EXERCISES (M): unary → server-streaming → error-status kata.
- QUIZ (S): 8 Q.
- MINI_PROJECT (M): CRUD service + bloom of 1 interceptor test.

### 30-event-sourcing
- THEORY (L): event store, CQRS, replay, snapshots, GDPR tension.
- CODE_DEEP_DIVE (M): expand 2.4KB Lab; event → aggregate → projector trace.
- EXERCISES (M): append + replay + idempotent projector with tests.
- QUIZ (M): 10 Q.
- MINI_PROJECT (L): ledger with snapshot + replay script.

### 31-mongodb
- THEORY (S): document model, BSON, index types, aggregation pipeline stages.
- CODE_DEEP_DIVE (S): annotate 5.3KB Lab; call out codec/registry.
- EXERCISES (M): CRUD + compound index + 2-stage agg with Testcontainers asserts.
- QUIZ (S): 10 Q.
- MINI_PROJECT (M): product catalog + text index + pagination.

### 32-redis
- THEORY (S): data structures, TTL/eviction, cache patterns, pub/sub vs streams.
- CODE_DEEP_DIVE (S): annotate 5.3KB Lab; flag Jedis vs Lettuce choice.
- EXERCISES (M): cache-aside + distributed lock skeleton + TTL test.
- QUIZ (S): 10 Q.
- MINI_PROJECT (M): leaderboard (ZSET) + rate limiter.

### 33-postgresql — template for DB modules
- THEORY (M): MVCC, isolation levels, EXPLAIN, index-only scans, connection pooling.
- CODE_DEEP_DIVE (S): annotate Lab + ExampleTest (best test sample in corpus).
- EXERCISES (S→M): promote ExampleTest to 3 tests (CRUD, txn rollback, Hikari tuning).
- QUIZ (S): 10 Q.
- MINI_PROJECT (M): orders schema + flyway V1 + 2 slow-query fixes.

### 34-rabbitmq
- THEORY (M): exchanges/queues/bindings, ack/nack, DLX, quorum queues.
- CODE_DEEP_DIVE (M): trace both Labs (top + nested) + SOLUTION diff.
- EXERCISES (M): direct→topic→DLQ progression with asserts (needs broker; Testcontainers).
- QUIZ (S): 10 Q.
- MINI_PROJECT (M): retry-with-backoff worker + DLQ dashboard notes.

### 35-consul
- THEORY (S): CP discovery, health checks, KV vs Config.
- CODE_DEEP_DIVE (S): annotate Lab; service registration lifecycle.
- EXERCISES (M): register + deregister + watch with test doubles.
- QUIZ (S): 8 Q.
- MINI_PROJECT (S): 2-service discovery demo (compose file + screenshot).

### 36-elasticsearch
- THEORY (M): inverted index, analyzers, mappings, relevance scoring.
- CODE_DEEP_DIVE (M): annotate 7.5KB nested Lab (largest in set).
- EXERCISES (M): index → match vs term → aggregation with Testcontainers.
- QUIZ (S): 8 Q.
- MINI_PROJECT (M): docs search with custom analyzer + relevance note.

### 37-keycloak
- THEORY (M): OIDC flows (code/PKCE/client-creds), JWT claims, realms/clients/roles.
- CODE_DEEP_DIVE (M): annotate Lab + exported `realm.json` sample (to add).
- EXERCISES (M): protect endpoint, test with WireMock/OIDC mock (no live server in unit test).
- QUIZ (S): 8 Q.
- MINI_PROJECT (M): SPA-code-flow diagram + 1 secured Spring endpoint.

### 38-prometheus
- THEORY (M): pull model, exposition format, PromQL basics, alerting rules.
- CODE_DEEP_DIVE (S): annotate 8KB Lab; counter vs gauge vs histogram callouts.
- EXERCISES (M): expose 3 metric types + 2 PromQL queries against fixture.
- QUIZ (S): 8 Q.
- MINI_PROJECT (S): `prometheus.yml` + 1 alert rule + screenshot.

### 39-grafana
- THEORY (S): dashboards-as-code, provisioning, Loki/Tempo plugin map.
- CODE_DEEP_DIVE (S): annotate Lab; dashboard JSON walkthrough (to add).
- EXERCISES (S): import + template variable + alert channel (file-only, no server needed).
- QUIZ (S): 6 Q.
- MINI_PROJECT (S): provisioned dashboard JSON for the 41-actuator app.

### 40-jaeger
- THEORY (S): trace/span model, sampling, context propagation (W3C).
- CODE_DEEP_DIVE (S): annotate Lab; 2-hop trace narrative.
- EXERCISES (M): add span + baggage + assert on in-memory exporter.
- QUIZ (S): 6 Q.
- MINI_PROJECT (S): screenshot + trace JSON of 41-actuator call.

### 41-actuator
- THEORY (S): endpoints, health groups, info contributors, Micrometer bridge.
- CODE_DEEP_DIVE (S): annotate Lab; custom HealthIndicator sample.
- EXERCISES (S): enable/disable endpoints + custom metric + MockMvc test.
- QUIZ (S): 6 Q.
- MINI_PROJECT (S): production-ready checklist demo feeding P4 modules.

### 42-testcontainers
- THEORY (M): docker lifecycle, reuse, waits, Ryuk; CI implications.
- CODE_DEEP_DIVE (M): annotate Lab; `@ServiceConnection` vs manual container.
- EXERCISES (M): postgres + kafka containers with 2 green tests (currently 0 tests).
- QUIZ (S): 8 Q.
- MINI_PROJECT (M): shared `ContainersBase` harness reused by 31/32/33.

### 43-wiremock
- THEORY (S): stub vs mock vs virtualize; record/playback.
- CODE_DEEP_DIVE (S): annotate 7.3KB Lab; scenario/stateful stub note.
- EXERCISES (M): 3 stubs (delay, fault, scenario) + 1 contract test.
- QUIZ (S): 6 Q.
- MINI_PROJECT (S): stub an OAuth token endpoint for 37-keycloak tests.

### 44-jmeter / 45-gatling (pair; do Gatling deep, JMeter baseline)
- THEORY (M each): workload models, percentiles vs averages, saturation signals.
- CODE_DEEP_DIVE (M each): annotate Lab; explain thread/arrival model + thresholds.
- EXERCISES (M each): run 50-VU baseline locally, save report HTML (not in CI).
- QUIZ (S each): 6 Q.
- MINI_PROJECT (M each): baseline report + 3 findings + 1 tuning.

### 46-flyway
- THEORY (S): versioned vs repeatable, baseline/repair, validate vs migrate.
- CODE_DEEP_DIVE (S): annotate Lab + add `V1__init.sql` sample walkthrough.
- EXERCISES (M): write V1+V2, simulate failed migration + repair.
- QUIZ (S): 6 Q.
- MINI_PROJECT (S): migrate the 33-postgresql orders schema.

### 47-liquibase
- THEORY (S): changelog formats, contexts/labels, rollback modes.
- CODE_DEEP_DIVE (M): annotate 8.9KB Lab (deepest in DB group).
- EXERCISES (M): XML→YAML conversion + rollback test.
- QUIZ (S): 6 Q.
- MINI_PROJECT (S): mirror of 46 MINI_PROJECT for compare/contrast table.

### 48-cucumber
- THEORY (S): Gherkin, glue, World/state, living docs.
- CODE_DEEP_DIVE (M): annotate CucumberLab + 1 `.feature` sample (to add).
- EXERCISES (M): write 2 scenarios + stepdefs + green run.
- QUIZ (S): 6 Q.
- MINI_PROJECT (M): checkout feature (happy + edge) reusing 50-junit5 asserts.

### 49-selenide
- THEORY (M): headless CI, selectors, flaky-test triage.
- CODE_DEEP_DIVE (M): annotate 1.3KB Lab; page-object sketch.
- EXERCISES (M): 2 specs (form + list filter) headless-only.
- QUIZ (S): 6 Q.
- MINI_PROJECT (M): 2-page flow video/screenshot + CI profile.

### 50-junit5
- THEORY (S): lifecycle, nested/params, extensions, AssertJ pairing.
- CODE_DEEP_DIVE (M): annotate both Labs; extension example (to add).
- EXERCISES (M): 5 katas (params, tempdir, timeout, extension, ordered).
- QUIZ (S): 8 Q.
- MINI_PROJECT (S): kata suite that other modules import as style guide.

### 51-quarkus / 52-micronaut / 53-helidon / 54-vertx
- THEORY (S/M): 51 M (CDI+Panache+DevServices); 52 S; 53 S; 54 M (event-loop, backpressure).
- CODE_DEEP_DIVE (S/M): annotate thin Labs (1.1–1.5KB); add 1 REST endpoint diff each.
- EXERCISES (M each): `@QuarkusTest` / `@MicronautTest` / Helidon MP test / Vert.x `VertxExtension` — 1 green test each (currently 0).
- QUIZ (S each): 6–8 Q.
- MINI_PROJECT (S/M): 51 M (REST+Panache CRUD), 52/53 S (mirror CRUD), 54 M (fan-out client).

### 56-k8s
- THEORY (M): pods/svcs/ingress, probes, limits, ConfigMaps/Secrets.
- CODE_DEEP_DIVE (M): extract PROJECTS.md yaml into `k8s/` + explain.
- EXERCISES (M): kind deploy + rollout + log triage (local-only).
- QUIZ (S): 8 Q.
- MINI_PROJECT (L): deploy 1 app (51 or 54) with HPA + probe proof.

### 57-service-mesh
- THEORY (M): sidecars, mTLS, traffic split, observability tap.
- CODE_DEEP_DIVE (S): annotate 1.2KB Lab + VirtualService/DestinationRule yaml (to add).
- EXERCISES (S): canary 90/10 + fault injection (spec-only if no cluster).
- QUIZ (S): 6 Q.
- MINI_PROJECT (M): canary demo doc building on 56.

### 58-serverless
- THEORY (S): FaaS constraints, cold starts, event shapes.
- CODE_DEEP_DIVE (S): annotate 1.3KB Lab; http vs event signature.
- EXERCISES (S): 2 functions (http + pubsub) with unit tests.
- QUIZ (S): 6 Q.
- MINI_PROJECT (S): deploy-notes + cost/latency table.

### 59-webassembly
- THEORY (S): WASM/WASI, grains of truth vs hype for Java devs.
- CODE_DEEP_DIVE (S): annotate 1.3KB Lab; Chicory/GraalWasm note.
- EXERCISES (S): run hello + pass a string/number boundary.
- QUIZ (S): 6 Q.
- MINI_PROJECT (S): 1-page decision memo (when NOT to use WASM).

### java-master-lab (meta, not a stub)
- Do NOT add THEORY/QUIZ per root. Instead: dedupe 112 top-level docs into `MASTER_INDEX.md` links, archive stale FINAL_*_SUMMARY reports, point capstone at real modules. Est M.
- If labs/ gets code later, require the same 5-artifact template before accepting.

### quarkus-learning/quarkus-getting-started (reference impl)
- Keep as-is (upstream scaffold). Add thin pedagogy wrapper only: THEORY S (Quarkus pitch + Dev Services), EXERCISES S (3 guided edits to GreetingResource), QUIZ S (6 Q), MINI_PROJECT S (add `/hello/{name}` + test). Est S total. Do not fork quarkus BOM.

## 4. Cross-cutting fixes (do once, benefit all)

1. **Pin `spring-boot-maven-plugin` version** in `java-learning-parent` pluginManagement — clears validate warnings in ~30 submodules. Est S.
2. **Standard 5-file template** per module: `THEORY.md` / `CODE_DEEP_DIVE.md` / `EXERCISES.md` / `QUIZ.md` (+ answers) / `MINI_PROJECT.md`, plus `README.md` pointer. Copy headers from 02-spring-ecosystem. Est S.
3. **Wire SOLUTION/ to tests**: move `SOLUTION/Test.java` content into `src/test` so `mvn test` actually runs; keep SOLUTION as reference only. Start with 33, 50, 42. Est M.
4. **Testcontainers harness** (42) reused by 31/32/33/36/46/47 — one `ContainersBase`, not six copies. Est M.
5. **Docker-gated minerals**: 34/36/37/44/45/56/57 MINI_PROJECTs must run without docker in CI (file/yaml/spec only); docker steps marked `[local-only]`. Est S (docs convention).

## 5. Suggested build order (sprints)

- Sprint 1 (P0): 33 → 32 → 31 → 50 → 41 → 46 → cross-fix #1+#2.
- Sprint 2 (P1): 42 → 47 → 43 → 48 → 44/45 (one deep, one baseline) → 49 → cross-fix #3+#4.
- Sprint 3 (P2): 55 → 34 → 27 → 28 → 29 → 30 → 36.
- Sprint 4 (P3): 02 close-out → 51 → 54 → 52/53 → getting-started wrapper → 56 → 57 → 58.
- Sprint 5 (P4): 38 → 39 → 40 → 23 → 35 → 37 → 26 → 24/25/59 spikes → java-master-lab dedupe.
