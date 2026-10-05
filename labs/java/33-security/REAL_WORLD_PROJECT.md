# REAL-WORLD PROJECT — Security: Leaked JWT Secret + SQLi Breach

## Incident Scenario
Attackers dump 40k user rows via `?search=` SQL injection, then forge admin
JWTs from a hardcoded secret found on GitHub. Ransom note arrives before the
CVE scan finishes.

## Symptoms
- `search=' OR '1'='1` returns full table; logs show `UNION SELECT` probes.
- JWTs accepted with `alg=none` and past `exp`; `aud/iss` unchecked.
- `AES/ECB` note-encryption with static key in `application.properties`.
- Secret `jwt.secret=changeme123` committed; same key in prod 2 years.
- `jcmd` attach open to all local users; heap dump contains tokens.

## Investigation Tasks
1. Contain first: rotate secret, revoke tokens, block IP, snapshot
   `jcmd <pid> GC.heap_dump` to a SECURE volume (tokens inside — restrict).
2. JFR: `jcmd <pid> JFR.start duration=120s filename=sec.jfr`; check
   `jdk.SocketRead` for exfil volume + `jdk.JavaExceptionThrow` auth errors.
3. Logs: `grep -E "OR 1=1|UNION SELECT|alg=none|401|403" app.log`; count
   forged-admin calls (`role=admin` from untrusted issuers).
4. Code audit: `grep -rn "createQuery(.*+\|Statement\|alg\|JwtParser\|ECB\|MD5" src/`;
   list every string-concatenated query and JWT verify call.
5. Threads/heap: `jcmd <pid> Thread.print` for active exfil sessions;
   heap-dump dominators for `String` tokens only in memory (do not print).
6. Repro (staging only): SQLi payload on clone, `alg=none` token, expired
   token replay — all must fail after fix, succeed before (record proof).
7. Supply chain: `dependency-check` + `git log -S changeme123` blast radius.

## Root Cause
Concatenated SQL + unverified JWTs (`none` accepted, no exp/aud check) +
ECB/static-key crypto + committed secret + missing WAF/rate-limit — classic
OWASP Top-10 stack with no boundary verification.

## Resolution
- Immediate: rotate + vault secrets, revoke sessions, parameterized queries
  hotfix, reject `none`/expired/aud-mismatch, force password reset, notify.
- Short-term: JPA bound params everywhere, JWT lib strict-verify, AES-GCM
  re-encrypt with KMS envelope, security headers, login rate-limit, ZAP gate.
- Long-term: STRIDE reviews, SAST/DAST + dep-scan in CI, secret-scanning
  pre-commit, key-rotation runbook, audit-log SIEM alerts.

## Runbook
```
1. Rotate secrets; revoke tokens; secure heap-dump handling.
2. Hotfix SQL concat + JWT strict-verify on canary; replay attacks fail.
3. Re-encrypt ECB data to GCM; purge committed secret from history.
4. ZAP + dep-scan green; enable auth-anomaly alerts.
5. Postmortem: breach notice + rotation/SBOM policy.
```

## Metrics
- Attack replays 0% success (20/20 blocked); ZAP High = 0.
- Secrets grep = 0 in repo; JWT strict-verify 100% (forged/expired/none out).
- Auth-anomaly alert fires < 5 min in drill; dep criticals = 0 untriaged.

---
## Sourced field notes (fetched Oct 2026 — verify before citing)
- JCA standard names (ciphers/hashes): https://docs.oracle.com/en/java/javase/21/docs/specs/security/standard-names.html
- JCE package: https://docs.oracle.com/en/java/javase/21/docs/api/java.base/javax/crypto/package-summary.html
