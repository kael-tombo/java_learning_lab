# SAST & DAST — Flashcards

---

## SAST Fundamentals

**Q: What is SAST (Static Application Security Testing)?**
**A:** White-box analysis of source code/bytecode without execution. Finds vulnerabilities early in SDLC. High false positive rate.

---

**Q: What is DAST (Dynamic Application Security Testing)?**
**A:** Black-box testing of running application from outside. Finds runtime vulnerabilities (config, auth, business logic). Slow, late, no code visibility.

---

**Q: What is IAST (Interactive Application Security Testing)?**
**A:** Instruments running app (agent/profiler). Combines SAST code visibility + DAST runtime confirmation. Low false positives. Runs in staging/QA.

---

**Q: What is SCA (Software Composition Analysis)?**
**A:** Scans dependencies (package.json, pom.xml, etc.) for known CVEs, license issues, outdated versions. Analyzes *third-party* code you depend on.

---

**Q: What are the three key concepts in SAST data flow analysis?**
**A:** Source (untrusted input), Sink (vulnerable operation), Sanitizer (neutralizes taint).

---

**Q: What is taint tracking?**
**A:** Marks data from sources, propagates through program, flags if reaches sink without sanitizer. Detects SQLi, XSS, Command Injection, Path Traversal, XXE, Deserialization, SSRF.

---

**Q: What is a source in SAST?**
**A:** Where untrusted data enters: HTTP params, headers, cookies, DB, files, env vars, message queues.

---

**Q: What is a sink in SAST?**
**A:** Where tainted data causes vulnerability: SQL execute, HTML/JS output, shell exec, eval, deserialize, file write, LDAP query, XPath.

---

**Q: What is a sanitizer in SAST?**
**A:** Function that neutralizes taint: parameterized queries, HTML/JS encoders, path normalizers, allowlist validators, safe APIs.

---

## False Positives & Tuning

**Q: Why does SAST have high false positives?**
**A:** No runtime context — doesn't know actual inputs, config, auth state, business logic. Flags all theoretical paths.

---

**Q: How do you tune SAST to reduce false positives?**
**A:** 1) Baseline (suppress existing FPs) 2) Custom rules for internal frameworks 3) Focus on high-confidence rules 4) Data flow depth limits 5) Confirm with DAST/IAST

---

**Q: What is a baseline in SAST?**
**A:** Suppress all current findings (mark as "accepted risk" or "FP"). Only fail build on *new* findings. Prevents alert fatigue.

---

**Q: What is the difference between a false positive and false negative?**
**A:** FP = flagged but not exploitable (wastes time). FN = missed vulnerability (worst case — attacker finds it).

---

## DAST Fundamentals

**Q: How does DAST discover attack surface?**
**A:** Crawls app: follows links, submits forms, parses JS, analyzes sitemap, uses OpenAPI/Swagger.

---

**Q: What are DAST blind spots?**
**A:** Authenticated areas, multi-step flows, SPA/client-side logic, API without UI links, rate-limited paths, business logic flaws.

---

**Q: How do you test authenticated areas with DAST?**
**A:** Provide valid session/cookies, login script, or OpenAPI with auth. Scan must maintain session.

---

**Q: What is a DAST "scan policy"?**
**A:** Configuration of tests to run: SQLi, XSS, Command Injection, Path Traversal, XXE, SSRF, Auth bypass, Rate limiting, Headers.

---

## Shift-Left & CI/CD

**Q: What is "shift-left" security?**
**A:** Move security earlier in SDLC. SAST in IDE → Pre-commit → PR → CI. DAST in staging gate. Cost to fix increases 10x per stage.

---

**Q: Where should SAST run in CI/CD?**
**A:** 1) IDE (real-time) 2) Pre-commit (fast subset) 3) PR gate (full, block on new Critical/High) 4) Build pipeline (gate to deploy)

---

**Q: Where should DAST run in CI/CD?**
**A:** Staging deployment gate (after deploy, before promote to prod). Scheduled prod scans. Too slow for PR.

---

**Q: Where should SCA run in CI/CD?**
**A:** Every build (fast). PR gate on new Critical/High in direct deps. Deep scan (transitive) nightly.

---

**Q: What is a security gate policy?**
**A:** Rules for blocking/failing: Block on new Critical/High SAST/SCA. Warn on Medium. DAST → ticket, not block.

---

## Secrets Detection

**Q: How does secrets detection differ from vulnerability detection?**
**A:** No sink — secret itself is vuln. Must scan git history. Requires rotation, not code fix. High FPs (test keys, placeholders).

---

**Q: What tools detect secrets in git history?**
**A:** truffleHog, Gitleaks, git-secrets, GitHub secret scanning, GitLab secret detection.

---

**Q: How do you prevent secrets in commits?**
**A:** Pre-commit hooks (git-secrets, talisman), push protection (GitHub/GitLab), CI scanning, developer education.

---

## Threat Modeling Flashcards

**Q: What threat does SAST-only strategy enable?**
**A:** Misses runtime vulnerabilities (config, env, auth, business logic) → production exploits.

---

**Q: What threat does DAST-only strategy enable?**
**A:** Vulnerabilities reach prod → expensive late fixes, no shift-left, missed unexercised code paths.

---

**Q: What threat does high SAST false positive rate enable?**
**A:** Alert fatigue → developers ignore/override findings → real vulnerabilities shipped.

---

**Q: What threat does missing baseline enable?**
**A:** Legacy findings flood every build → noise → gate disabled.

---

**Q: What threat does missing sanitizer modeling enable?**
**A:** False positives on safe code (sanitized but SAST doesn't know) → distrust in tool.

---

**Q: What threat does missing source/sink modeling enable?**
**A:** False negatives — vulnerabilities in custom frameworks/patterns not detected.

---

**Q: What threat does unauthenticated DAST enable?**
**A:** Most attack surface untested (authenticated areas) → critical flaws missed.

---

**Q: What threat does missing SCA enable?**
**A:** Supply chain attacks (compromised dependency) → zero-day in your app via third-party code.

---

**Q: What threat does slow security gates enable?**
**A:** Developers bypass (skip, force push) → no security checking.

---

**Q: What threat does secrets in git history enable?**
**A:** Attacker scans public repos → finds API keys, DB passwords, cloud credentials → full compromise.