# SAST & DAST — Hands-On Exercises

**Hardening & Debugging Tasks** — Each exercise includes a vulnerable/broken implementation to fix, a debugging challenge, or a threat-modeling scenario.

---

## Exercise 1: SAST Taint Tracking — Custom Sanitizer Registration

**File**: `src/main/java/com/security/deep/lab04/CustomSanitizer.java`

**Scenario**: Your SAST tool flags XSS in `HtmlUtils.safeRender(userInput)` but `safeRender` is a custom sanitizer that properly encodes HTML. The tool doesn't know this.

**Task**:
1. Run SAST on codebase — observe false positive on `safeRender`
2. Implement custom sanitizer registration for your SAST tool (Semgrep/CodeQL/Checkmarx config)
3. Register `HtmlUtils.safeRender` as HTML sanitizer (removes HTML taint)
4. Register `SqlUtils.paramQuery` as SQL sanitizer (removes SQL taint)
5. Re-run SAST — false positives gone, true positives remain
6. Test: add new sanitizer `JsonUtils.escape` for JSON sink

**Threat Model**: Developers ignore SAST due to false positives on known-safe code. Custom sanitizers must be modeled or FPs persist.

**Verification**: Known-safe sanitized calls no longer flagged; unsanitized sinks still flagged.

---

## Exercise 2: SAST False Negative — Missing Sink in Custom Framework

**File**: `src/main/java/com/security/deep/lab04/MissingSink.java`

**Scenario**: Your framework has `Database.executeRaw(sql, params)` which is safe, but `Database.executeUnsafe(sql)` concatenates params. SAST only knows standard sinks (`PreparedStatement.execute`).

**Task**:
1. Write code using `Database.executeUnsafe(userInput)` — SAST misses it
2. Implement custom sink definition for `Database.executeUnsafe`
3. Re-run SAST — vulnerability now detected
4. Test: `executeRaw` with param binding not flagged; `executeUnsafe` flagged

**Threat Model**: Custom frameworks bypass SAST sink detection. Attackers find these gaps. Must model all dangerous APIs.

**Verification**: Custom unsafe API detected; safe API not flagged.

---

## Exercise 3: Secrets Detection — Git History Scanning

**File**: `src/main/java/com/security/deep/lab04/SecretsHistory.java`

**Scenario**: Developer committed AWS keys 50 commits ago, then "removed" them in a later commit. Keys still in git history.

**Task**:
1. Create test repo with: commit 1 (add keys), commit 2-50 (other changes), commit 51 (remove keys)
2. Run secrets scanner (truffleHog/Gitleaks) on current HEAD — no findings
3. Run scanner on full history — finds keys in commit 1
4. Implement pre-commit hook that scans staged changes + history
5. Implement CI check that fails build if secrets in history
6. Test: new commit with key blocked; existing history flagged for rotation

**Threat Model**: Attackers scan public git history for secrets. "Deleted" secrets are still accessible. Rotation required, not just removal.

**Verification**: Keys detected in history; pre-commit blocks new secrets; CI flags existing.

---

## Exercise 4: DAST Authenticated Scan — Session Handling

**File**: `src/main/java/com/security/deep/lab04/DastAuth.java`

**Scenario**: DAST scanner fails to maintain session — logs in, gets cookie, but subsequent requests don't send cookie. Only public pages scanned.

**Task**:
1. Configure DAST (OWASP ZAP/Burp) with login script: POST /login → extract session cookie
2. Implement session management: cookie jar, CSRF token extraction, re-login on 401
3. Verify authenticated crawl reaches: /admin, /profile, /settings, /api/user/data
4. Test: scan with auth finds 5x more endpoints than without

**Threat Model**: Most vulnerabilities are in authenticated functionality. Unauthenticated DAST misses 80%+ of attack surface.

**Verification**: Authenticated endpoints crawled; session maintained across requests; re-login works.

---

## Exercise 5: DAST Business Logic Test — Price Manipulation

**File**: `src/main/java/com/security/deep/lab04/PriceManipulation.java`

**Scenario**: E-commerce app has checkout flow: add to cart → set quantity → apply coupon → pay. DAST doesn't understand negative quantity or coupon stacking.

**Task**:
1. Write custom DAST script (ZAP Active Scan Rule / Burp BCheck) for:
   - Negative quantity in cart API
   - Coupon applied multiple times
   - Price parameter tampering (hidden field)
   - Race condition: concurrent coupon applications
2. Run against test app — verify findings
3. Fix: server-side validation (quantity > 0, coupon single-use, price from DB)
4. Re-run — all logic flaws blocked

**Threat Model**: Attackers manipulate business logic, not just inject payloads. Standard DAST signatures miss these. Custom scripts required.

**Verification**: All 4 logic flaws detected and confirmed fixed.

---

## Exercise 6: IAST Instrumentation — Runtime Confirmation

**File**: `src/main/java/com/security/deep/lab04/IastInstrumentation.java`

**Scenario**: SAST flags potential SQLi in complex data flow. Need IAST to confirm if actually exploitable at runtime.

**Task**:
1. Deploy app with IAST agent (Contrast/Seeker/Hdiv)
2. Run functional tests / DAST scan against instrumented app
3. IAST reports: which SAST findings confirmed (taint reached sink at runtime)
4. Correlate: SAST finding ID ↔ IAST confirmation
5. Prioritize: Confirmed > High Confidence SAST > Unconfirmed
6. Test: 10 SAST findings → 3 confirmed by IAST → fix those first

**Threat Model**: SAST noise overwhelming. IAST confirms exploitability in running app. Fix confirmed first.

**Verification**: IAST confirms true positives; unconfirmed SAST findings deprioritized.

---

## Exercise 7: SCA Dependency Confusion — Internal Package Hijack

**File**: `src/main/java/com/security/deep/lab04/DependencyConfusion.java`

**Scenario**: Your company uses internal package `@corp/utils` v1.0.0. Attacker publishes `@corp/utils` v99.9.9 to public npm. Build pulls public version.

**Task**:
1. Configure package manager (npm/Maven/Gradle) to prefer private registry for `@corp/*` scope
2. Implement SCA check: verify all internal packages resolve to private registry
3. Test: publish fake higher version to public registry — build fails or uses private
4. Implement: `npmrc` / `settings.xml` with strict registry priority
5. Test: dependency confusion attack blocked

**Threat Model**: Dependency confusion (Alex Birsan) — public registry wins on version. Internal packages must be scoped and registry-pinned.

**Verification**: Internal packages only from private registry; public higher versions ignored.

---

## Exercise 8: SCA Transitive Vulnerability — Reachability Analysis

**File**: `src/main/java/com/security/deep/lab04/TransitiveReachability.java`

**Scenario**: SCA flags CVE-2022-1234 in `commons-io:2.6` (transitive, 5 levels deep). But your code never calls the vulnerable method.

**Task**:
1. Run SCA with reachability analysis (OSS Index, Sonatype, Endor Labs)
2. Determine: is vulnerable method actually reachable from your code?
3. If not reachable: mark as "not exploitable" with evidence
4. If reachable: prioritize upgrade
5. Test: 50 transitive CVEs → 45 not reachable → 5 actionable

**Threat Model**: Transitive vulns flood backlog. Reachability separates theoretical from exploitable. Focus on callable paths.

**Verification**: Reachability analysis correctly identifies callable vs non-callable vulns.

---

## Exercise 9: CI/CD Security Gate — Policy Enforcement

**File**: `src/main/java/com/security/deep/lab04/CiCdGate.java`

**Scenario**: PR merged with Critical SAST finding because gate was "warn only." Need enforceable gate.

**Task**:
1. Define policy as code (OPA/Rego or GitHub Actions rules):
   - Block PR on: new Critical/High SAST, new Critical/High SCA (direct), secrets in diff
   - Warn on: new Medium SAST, SCA transitive Critical
   - Require: DAST scan on staging before prod deploy
2. Implement in CI: GitHub Actions / GitLab CI / Jenkins
3. Test: PR with new Critical SAST → blocked; PR with only Medium → passes with warning
4. Add: "security approval" required for exceptions (with audit trail)

**Threat Model**: Developers bypass warnings. Gates must block with override requiring explicit approval.

**Verification**: Policy blocks violating PRs; exceptions audited; staging gate runs DAST.

---

## Exercise 10: Design a SAST/DAST/SCA/IAST Threat Model

**File**: `docs/threat-model-sast-dast.md` (create this)

**Scenario**: You're building an AppSec program for a fintech with 200 developers, 50 microservices, 10 SPAs, mobile apps, and strict compliance (PCI DSS, SOX).

**Task**:
1. **Assets**: Source code, build artifacts, dependencies, secrets, test data, scan results, compliance evidence
2. **Adversaries**: 
   - Developer (accidental vuln introduction)
   - Malicious insider (backdoor in code)
   - Supply chain attacker (compromised dependency)
   - CI/CD compromise (injected artifact)
   - Scanner evasion (obfuscated vuln)
3. **Trust Boundaries**: IDE → Git → CI → Artifact Registry → Staging → Prod
4. **Tool Coverage Map**:
   - SAST: Every PR, every language, custom rules for frameworks
   - SCA: Every build, direct + transitive, reachability, license
   - Secrets: Pre-commit, push protection, CI, git history
   - IAST: Staging, all services, correlated with SAST
   - DAST: Staging gate, authenticated, custom logic scripts
   - Pen Test: Quarterly, authenticated, business logic focus
5. **Per-Tool Threats & Mitigations**:
   - SAST: FP fatigue → baseline, custom rules, PR-only new findings
   - SAST: FN custom sinks → framework modeling, regular audit
   - DAST: Blind spots → OpenAPI, auth scripts, custom checks
   - SCA: Transitive noise → reachability, private registry pinning
   - Secrets: History leakage → push protection, rotation automation
   - IAST: Prod risk → staging only, sampling, performance budget
6. **Metrics & SLAs**:
   - SAST: New Critical fixed < 24h, High < 7d
   - SCA: Critical direct < 24h, reachable transitive < 7d
   - Secrets: Rotation < 1h after detection
   - DAST: Critical confirmed < 7d
7. **Compliance Evidence**: Automated report generation for auditors

**Deliverable**: `THREAT_MODEL.md` with STRIDE per tool, data flows, coverage matrix, SLA definitions, exception process, tool config as code.