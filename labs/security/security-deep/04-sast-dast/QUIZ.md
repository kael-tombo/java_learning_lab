# SAST & DAST — Quiz

**10 Questions with Answers & Threat-Model Reasoning**

---

### Q1: What is the fundamental difference between SAST and DAST in terms of visibility and timing?

**Answer**: 
- **SAST (White-Box)**: Analyzes source code/bytecode *without executing*. Runs early (IDE, CI/CD). Sees code structure, data flow, control flow. Misses runtime config, env vars, business logic.
- **DAST (Black-Box)**: Tests *running application* from outside. Runs late (staging/prod). Sees actual behavior, runtime config, auth flows. Misses code internals, unexercised paths.

**Threat-Model Reasoning**: SAST catches bugs before deploy (shift-left) but has high false positives (no runtime context). DAST catches exploitable issues in deployed app but is slow, late, and can't see unexercised code. Threat model: SAST prevents vulnerabilities from reaching prod; DAST catches what SAST misses (config, runtime, logic). Both needed — neither sufficient alone.

---

### Q2: What is "taint tracking" in SAST, and what vulnerability classes does it detect?

**Answer**: Taint tracking marks untrusted inputs (sources: HTTP params, DB, files) and tracks data flow through the program to sensitive sinks (SQL exec, HTML output, shell exec, deserialization). Detects: SQLi, XSS, Command Injection, Path Traversal, XXE, Deserialization, SSRF.

**Threat-Model Reasoning**: Taint tracking models attacker-controlled data flow. Threat: attacker controls source → data reaches sink without sanitization → vulnerability. SAST must model: sanitizers (breaks taint), propagators (passes taint), sinks (vulnerability if tainted). False positives from unknown sanitizers; false negatives from missed sources/sinks.

---

### Q3: Why does SAST have high false positive rates, and how do you tune it?

**Answer**: SAST lacks runtime context: doesn't know actual input values, config, authentication state, business logic. Flags all theoretical paths. Tuning: 1) Suppress known FPs (baseline), 2) Custom rules for internal frameworks, 3) Focus on high-confidence rules (SQLi, XSS), 4) Use data flow depth limits, 5) Integrate with DAST for confirmation.

**Threat-Model Reasoning**: False positives waste developer time → alert fatigue → real issues ignored. Threat model: developer ignores SAST because "it's always noise." Mitigation: baseline (suppress existing FPs), only fail build on *new* high-severity findings, provide actionable fix guidance, measure FP rate and reduce it.

---

### Q4: What is the difference between a "source," "sink," and "sanitizer" in SAST data flow analysis?

**Answer**: 
- **Source**: Where untrusted data enters (request params, headers, cookies, DB, files, env vars)
- **Sink**: Where tainted data causes vulnerability (SQL execute, HTML render, eval, exec, deserialize, file write)
- **Sanitizer**: Function that neutralizes taint (parameterized query, HTML encoder, path normalizer, allowlist validator)

**Threat-Model Reasoning**: Taint flows: Source → [Propagators] → Sink = Vulnerability. Sanitizer breaks chain. Threat model: attacker controls Source. If no Sanitizer before Sink, exploit possible. SAST must know all three for each language/framework. Missing sanitizer = FP; missing source/sink = FN.

---

### Q5: How does DAST discover attack surface, and what are its blind spots?

**Answer**: DAST crawls application: follows links, submits forms, parses JS, analyzes sitemap, uses OpenAPI/Swagger. Blind spots: 
- Authenticated areas (needs valid session)
- Multi-step flows (wizard, checkout)
- Client-side logic (SPA routes, WASM)
- API endpoints without UI links
- Rate-limited/blocked paths
- Business logic flaws (price manipulation, workflow bypass)

**Threat-Model Reasoning**: DAST sees what a user sees. Threat model: attacker has valid credentials (credential stuffing, phishing). DAST must test authenticated. Blind spots = untested attack surface. Mitigation: provide authenticated session, OpenAPI spec, seed data, custom scan scripts for business logic.

---

### Q6: What is IAST (Interactive Application Security Testing) and how does it combine SAST+DAST?

**Answer**: IAST instruments running application (Java agent, .NET profiler, Node hook). Observes actual code execution during DAST/manual testing. Maps runtime behavior to source code lines. Benefits: 
- Confirms exploitability (DAST) + shows exact code location (SAST)
- Low false positives (only reports exercised paths)
- Detects runtime-only issues (config, env)

**Threat-Model Reasoning**: IAST addresses the SAST/DAST gap. Threat model: attacker exploits running app. IAST sees *actual* data flow during attack. More accurate but requires instrumentation (performance overhead, production risk). Best in staging/QA.

---

### Q7: What is the "shift-left" strategy, and where does SAST fit?

**Answer**: Shift-left = move security earlier in SDLC. SAST in: 
1. IDE (real-time feedback) 
2. Pre-commit hook (fast subset) 
3. Pull Request (full scan, block merge on new critical) 
4. CI/CD pipeline (gate to deploy)
DAST in: Staging deployment gate, scheduled prod scans.

**Threat-Model Reasoning**: Cost to fix: IDE $1, PR $10, CI $100, Staging $1000, Prod $10000+. Threat model: vulnerabilities introduced during coding. Earlier detection = cheaper fix. SAST enables shift-left; DAST validates in runtime context.

---

### Q8: How do you handle secrets detection in SAST, and why is it different from vulnerability detection?

**Answer**: Secrets detection (API keys, passwords, tokens, private keys) uses entropy/regex matching, not taint tracking. Different because: 
- No "sink" — secret itself is the vulnerability
- Must detect in history (git), not just current code
- Rotation required, not code fix
- High false positives (test keys, examples, placeholders)

**Threat-Model Reasoning**: Threat: secret committed → attacker scans GitHub/GitLab → uses secret. SAST must scan *entire history* (git-secrets, truffleHog, Gitleaks). Mitigation: pre-commit hooks, push protection (GitHub), secret scanning in CI, rotation automation.

---

### Q9: What is SCA (Software Composition Analysis) and how does it complement SAST/DAST?

**Answer**: SCA scans dependencies (package.json, pom.xml, go.mod, requirements.txt) for known vulnerabilities (CVE in libraries). Checks: direct + transitive deps, license compliance, outdated versions. Complements: SAST/DAST analyze *your* code; SCA analyzes *others'* code you depend on. Supply chain attacks target dependencies.

**Threat-Model Reasoning**: Threat model: attacker compromises popular library (event-stream, ua-parser-js, Log4j) → all downstream apps vulnerable. SCA detects known vulnerable versions. Must run on every build, monitor for new CVEs in pinned versions, enforce policy (no Critical/High in prod).

---

### Q10: How do you design a CI/CD pipeline security gate that balances speed and coverage?

**Answer**: 
- **Fast gate (PR, <5 min)**: SAST (incremental), secrets scan, SCA (direct deps only), unit tests
- **Medium gate (Merge/Build, <30 min)**: Full SAST, full SCA, IAST (staging deploy + smoke test)
- **Slow gate (Nightly/Weekly, hours)**: DAST (full crawl), pen test (scheduled), dependency deep scan, license audit
- **Policy**: Block PR on *new* Critical/High SAST/SCA. Warn on Medium. DAST findings → ticket, not block (too slow).

**Threat-Model Reasoning**: Threat: slow gates → developers bypass (skip tests, force push). Fast gate catches obvious issues; deep gates catch complex issues. Threat model: attacker exploits gaps in coverage. Balance: gates developers accept + coverage attackers can't bypass.