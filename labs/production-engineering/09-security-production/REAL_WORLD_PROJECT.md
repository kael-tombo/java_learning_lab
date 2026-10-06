# Lab 09: Security Engineering in Production — Real World Project

## Scenario: "The Actuator That Was Supposed to Be Private"

You are a security engineer embedded in a fintech platform: 14 Spring Boot 3 services, Java 21, Kubernetes, an internal developer portal, and a security team of four.

**The incident** — Sunday 03:12. An external researcher emails your security address with a proof of concept: `https://api.yourcompany.com/actuator/env` returns your production configuration as JSON. The response contains a database hostname, an internal service URL, and — critically — a value under the key `legacy.api.key` whose name does not match Spring's redaction patterns, so it is printed in clear text. That key is a live third-party payment-gateway credential, scoped to that gateway only.

**What happened over 5 weeks**:

1. **03:12** — Report received. Triage confirms the finding on the production ingress.
2. **03:40** — Key rotated with the third party. No evidence of misuse.
3. **Next 2 weeks** — A broader audit discovers: 9 of 14 services expose actuator on the public ingress; 3 leak `/heapdump` (containing session tokens and customer PII); 11 log full request headers, so bearer tokens land in the log aggregator for 30 days; a developer committed an AWS access key to a repository 8 months ago, and it is still valid.
4. **The security team's finding**: there is no inventory of where secrets live, no dependency/SBOM capability, no CI security gate, and no defined authorization standard. Four engineers were covering 14 services.

**Your job over 4 weeks**: build a security baseline that survives contact with 14 teams who did not ask for it. Define the standard, ship the controls that are cheap and central, enforce the rest in CI, and produce an honest accepted-risk register.

**Time**: 30–40 hours | **Difficulty**: Advanced

---

## Phase 1 — Know what you have (Day 1–4)

### 1.1 Exposure inventory

For all 14 services, from inside the cluster *and* from outside:

| Check | Method | Result needed |
|---|---|---|
| Public ingress paths | External scan | every reachable path, with auth status |
| Actuator exposure | `curl` per service/port | endpoints and redaction status |
| Logged secrets | grep a 24 h log sample | token/password/cookie occurrences |
| Management port reachable | network test | yes/no per namespace |
| TLS posture | external TLS check | version, cipher, cert expiry, HSTS |

**Deliverable 1 — Exposure inventory** with a per-service table and a severity-ranked finding list. Include the `legacy.api.key` case study: why the redaction heuristic missed it.

### 1.2 Secret inventory

Find every credential that exists, where it is stored, who can read it, and how it is rotated. Sources: env vars in deployments, `application*.yml` (all profiles), Kubernetes Secrets, CI secrets, Vault paths, config repos, Slack bookmarks, runbooks, and the git history.

Classify each: `live-production`, `staging`, `rotated-never-deleted`, `hardcoded-in-repo`, `unknown-provenance`.

**Deliverable 2 — Secret register**: every secret with owner, location, readers, rotation cadence, and blast radius if leaked. Include the git-history key with the commit hash and the code search that found it.

### 1.3 Authorization matrix

For every endpoint on every service: path, HTTP method, authentication required, required authority, tenant scoping (yes/no), and whether the check is enforced in code or only by network position.

**Deliverable 3 — Authorization matrix** across all 14 services, with every `internal`-only endpoint and no-code-check called out. Prioritise the endpoints that mutate money or expose PII.

### 1.4 Threat model the platform

STRIDE per service class, with the top 3 assets and abuse cases named. Include supply chain as a first-class threat — the leaked AWS key shows it is real for you.

**Deliverable 4 — Threat model** with the top 5 platform-level threats and the control that addresses each.

---

## Phase 2 — Ship the cheap central controls (Day 4–9)

### 2.1 Ingress and actuator lockdown (one change, all services)

1. Ingress allow-list: only `/api/**`, `/actuator/health`, `/actuator/info`, `/actuator/prometheus` (internal allow-list source only). Everything else returns 404 at the edge.
2. Management port moved to a separate port bound to the pod IP, protected by a `NetworkPolicy` allowing only the monitoring namespace.
3. `management.endpoint.env.show-values: NEVER` **plus** renaming secrets so no key matches an obvious pattern *and* the env var is not populated from `SPRING_APPLICATION_JSON`.
4. Disable `env`, `heapdump`, `threaddump`, `loggers`, `mappings`, `shutdown` in every environment.

**Deliverable 5 — Hardened ingress + actuator config**, applied to all 14 services, with an external re-scan showing zero reachable sensitive endpoints.

### 2.2 Log hygiene (the cheapest large win)

- Drop request/response bodies and headers from all log statements.
- JSON logging with an allow-list of fields: timestamp, level, service, env, version, trace_id, request_id, error class, message.
- A `TurboFilter` scrubbing `authorization`, `cookie`, `password`, `token`, `card`, `ssn` patterns from message text.
- Rotate the third-party key already leaked into logs; treat the log aggregator's historical data as a store to be access-controlled and aged out.

**Deliverable 6 — Log scrubbing policy** + a grep result over a 24 h sample showing zero occurrences of the sensitive key names, before and after.

### 2.3 Secret handling

1. External secrets operator syncing from the existing vault into Kubernetes Secrets; `SecretStoreClass` replaces every hand-created secret.
2. Secrets mounted as files (memory-backed `emptyDir` where rotation matters), never env vars.
3. `etcd` encryption at rest verified; namespace RBAC restricted so only the owning service account can read its secret.
4. Migrate the highest-value credentials to short-lived dynamic ones: the AWS key → IRSA/Workload Identity; the payment gateway key → per-service credential with rotation.

**Deliverable 7 — Secret migration** with a before/after of the register, and evidence of rotation working (a rotated value observed by a running pod).

### 2.4 Identity baseline

- All services as OAuth2 resource servers with a shared issuer, algorithm pinned, `iss`/`aud`/`exp` validated, scopes mapped to authorities.
- `@EnableMethodSecurity` present everywhere; CI enforces it.
- `denyAll()` default in every `SecurityFilterChain`.
- Trust-all TLS grepped and removed platform-wide.

**Deliverable 8 — Identity baseline** applied to all 14 services, with the conformance report per service.

---

## Phase 3 — Supply chain (Week 2)

### 3.1 Inventory and scanning

- Generate an SBOM (CycloneDX) for every service artifact at build time; store it alongside the image.
- Dependency scanning in CI: fail on HIGH/CRITICAL with a known fix; route the rest to a backlog with an owner and a date.
- Container image scanning: base image pinned by digest, updated on a weekly base-image bump PR.
- Secret scanning across git history and CI logs, with a rotation playbook on any hit.

**Deliverable 9 — SBOM per artifact** + a measured "advisory to fleet impact" drill (see 3.2).

### 3.2 Advisory response drill

Pick a real published advisory affecting a popular Java library in your estate. Time yourself: advisory published → complete list of affected artifacts and images → owner notified → patched. Record the minutes at each step.

**Deliverable 10 — Advisory drill report** with the timeline and the bottleneck step. Set the remediation SLO from the result (e.g. detect ≤ 1 h, patch ≤ 7 days for HIGH).

### 3.3 Build integrity

- Build once, promote the same image digest through all environments (no rebuild per stage).
- Sign images; verify at admission.
- CI secrets federated (OIDC), short-lived, per-job, never echoed.
- Branch protection: no force-push, required reviews, required status checks including the security gate.

**Deliverable 11 — Build integrity controls** with a red-team self-test: attempt a tag mutation and a dependency-confusion resolution, and show both blocked.

---

## Phase 4 — CI enforcement (Week 2–3)

Ship gates that developers experience as fast, specific, and fixable:

| Gate | Fails on | Target runtime |
|---|---|---|
| Dependency scan | HIGH/CRITICAL CVE with a fix | < 60 s |
| Secret scan | any credential-shaped literal | < 15 s |
| SAST (Semgrep security rules) | injection, trust-all TLS, deserialization, unbounded pagination | < 60 s |
| Authorization coverage | mapped endpoint with no matcher and no `@PreAuthorize` | < 10 s |
| Header check | missing HSTS/CSP/nosniff configuration | < 10 s |
| Policy-as-code (OPA/conftest) | container running as root, no capability drop, writable rootfs | < 10 s |
| Integration security tests | the `SecurityRegressionTest` suite | < 5 min |

Requirements: every failure message names the file, line, the risk, and a fix. Every gate has a documented, time-boxed break-glass with an owner and expiry.

**Deliverable 12 — CI gate suite** merged with break-glass register, plus the red-team PRs (unauthorized endpoint, concatenated query, hardcoded secret, root container) all blocked with the specific message.

---

## Phase 5 — Prove it (Week 3)

Run a controlled, authorized security assessment of your own platform in staging, plus a production-shaped validation of the controls:

| Scenario | Method | Success criteria |
|---|---|---|
| S1 | External scan of every public ingress | zero reachable actuator/management paths; all headers present |
| S2 | Wrong-`aud`, wrong-`iss`, expired, `alg:none`, insufficient-scope tokens against every service | 401/403 in all cases; zero 200s |
| S3 | Tenant-isolation test: tenant A fetches tenant B's resources | 404 in all cases; no existence disclosure |
| S4 | Replay of the `actuator/env` finding | 404 at the edge; `env` disabled |
| S5 | Log capture over 10k requests | zero tokens/passwords/PII fields |
| S6 | Secret-exposure test: read `/proc/<pid>/environ` in a pod | no secret present; file mount only |
| S7 | Mass assignment and unbounded pagination fuzzing | rejected server-side |
| S8 | Tag-mutation and dependency-confusion attempt | blocked at admission / registry |
| S9 | Run the advisory drill again | detect ≤ 1 h, patch ≤ 7 days |
| S10 | Tabletop: leaked AWS key with production IAM role | rotation + blast-radius assessment in < 1 h |

**Deliverable 13 — Assessment report** with all ten scenarios, evidence, and the residual risks accepted.

---

## Phase 6 — Make it survive without you (Week 3–4)

- **Service template**: security baseline baked in — resource server, method security, denyAll, headers, actuator lockdown, mounted secrets, CI security job.
- **Security champions**: one engineer per team, trained on this baseline, given a 30-minute monthly office hour, empowered to block merges.
- **Runbooks**: leaked credential, exposed actuator, CVE advisory, suspicious log content, unauthorized-access investigation.
- **Accepted-risk register**: every known exception with owner, compensating control, expiry date, and review cadence.
- **Security review in PRR**: the production readiness review now includes an explicit security section.
- **Quarterly**: re-run the exposure inventory and the advisory drill; measure patch latency as a reported SLO.

**Deliverable 14 — Institutionalization package**: template diff, champion program, runbooks, accepted-risk register, PRR checklist.

---

## Phase 7 — Quantify and communicate (Week 4)

| Metric | Before | After |
|---|---|---|
| Services with public actuator | 9 / 14 | 0 / 14 |
| Services with credentials in logs | 11 / 14 | 0 / 14 |
| Endpoints with an enforced authority check | 61% | 100% |
| Secrets that are static and long-lived | 34 | 6 (rest dynamic/short-lived) |
| Hardcoded credentials in git history | 1 live | 0 live |
| Artifacts with an SBOM | 0 / 14 | 14 / 14 |
| Time from advisory to fleet impact list | ~3 days (manual guess) | < 15 min |
| Time from advisory to patched production | ~4 weeks | < 7 days |
| CI security gates | 0 | 7 |
| Externally reachable sensitive endpoints | 12 | 0 |
| Documented accepted risks | none | 5, each with owner + expiry |

Present this to engineering leadership together with the **accepted-risk register** and an explicit ask: headcount for the security team, or an explicit statement of which risks the business accepts. That conversation is the deliverable as much as the numbers are.

**Deliverable 15 — Business case + risk acceptance memo**, with the residual risks named and owned.

---

## Deliverables checklist

- [ ] Phase 1 exposure inventory, secret register, authorization matrix, threat model.
- [ ] Phase 2 ingress/actuator lockdown, log hygiene, secret migration, identity baseline.
- [ ] Phase 3 SBOM, advisory drill, build integrity.
- [ ] Phase 4 seven CI gates + break-glass register.
- [ ] Phase 5 ten-scenario assessment report.
- [ ] Phase 6 template, champions, runbooks, accepted-risk register.
- [ ] Phase 7 before/after business case + risk acceptance memo.

---

## Rubric

| Dimension | Weak | Strong |
|---|---|---|
| Discovery | "We have security scanning" | External + internal exposure inventory, secret register, authorization matrix, threat model |
| Identity | "JWTs are signed so we're fine" | Algorithm pinning, claim validation tests, scopes→authorities, denyAll default |
| Secrets | "We use Kubernetes Secrets" | Vault-synced, file-mounted, RBAC-restricted, dynamic where possible, rotation proven |
| Logs | "We redacted the fields" | Allow-list logging + scrub filter + grep evidence over 24 h |
| Supply chain | "Trivy runs in CI" | SBOM per artifact + measured advisory-response drill + provenance/signing |
| Enforcement | "Security is in the checklist" | 7 fast CI gates with specific messages, break-glass with expiry |
| Proof | "We ran a scan" | Ten scenarios including wrong-audience, tenant isolation, tag mutation, tabletop key leak |
| Sustainability | "The security team enforces this" | Template, champions, runbooks, accepted-risk register, quarterly re-measure |
| Communication | Technical only | Before/after numbers plus an explicit risk-acceptance ask to leadership |

---

## Sourced field notes (fetched Oct 2026 — verify before citing)

1. **OWASP Cheat Sheet Series (Spring Security / REST Security / Secrets Management)** — https://cheatsheetseries.owasp.org/ — the practical baseline for the controls in Phases 2–4. Specific pages to cite rather than the index: `cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html` (authz, rate limiting, input validation), `cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html` (secret storage and rotation), and `cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html` (what must never be logged). Verify current OWASP Top 10 numbering before mapping your findings to categories.
2. **Kubernetes — `concepts/security/secrets` and `concepts/security/pod-security-standards`** — https://kubernetes.io/docs/concepts/security/secrets/ — the authoritative statement that Kubernetes Secrets are base64-encoded and **not** encrypted by default, plus the guidance on enabling `etcd` encryption at rest, restricting secret access via RBAC, and mounting secrets as files rather than environment variables. Also the Pod Security Standards page for the `runAsNonRoot`, capability-drop, and seccomp requirements your policy-as-code gate should enforce.

Additional anchors worth verifying: the exact `management.endpoint.env.show-values` and redaction-key behaviour for your Spring Boot 3.x version (it has changed across minors), the current recommended JWT algorithm pinning approach in Spring Security 6, NIST SP 800-63B password guidance (verify the current minimum length and blocklist requirements rather than quoting from memory), and CycloneDX/Syft output format support in your scanner.

---

## Reflection questions

1. The researcher found `legacy.api.key` because its name didn't match the redaction heuristic. What is the structural fix that does not depend on naming conventions?
2. Eleven services were logging bearer tokens. Why does this keep happening despite security reviews, and what change to the default logging pattern would prevent it forever?
3. You have four security engineers and fourteen teams. Which controls are only worth building centrally, and which must be adopted by each team?
4. The git-history key was eight months old and still valid. What is the cheapest process change that would have caught it in a week?
5. Which risks in your accepted-risk register would you escalate to leadership, and what would you ask for?
