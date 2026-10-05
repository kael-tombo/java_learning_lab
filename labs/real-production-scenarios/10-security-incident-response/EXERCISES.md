# EXERCISES — Lab 10: Security Response

## Exercise 1: Scope in 10 Min (15 min)
Given IdP + audit excerpts, list compromised accounts, keys, hosts. Output blast-radius table.

## Exercise 2: Revoke Everything (20 min)
Rotate key in manager, revoke tokens/sessions, force re-auth. Verify old token 401s (curl).

## Exercise 3: Isolate Workload (15 min)
NetworkPolicy deny-all + quarantine label + scale bad deploy to 0. Verify no egress (flow log/curl timeout).

## Exercise 4: JWT Audit (20 min)
Find `alg:none`/no-exp/no-aud in sample validator; fix + test forged/expired rejected.

## Exercise 5: TLS Check (15 min)
`openssl s_client` + `curl -v` diagnose expiry/mismatch; document rotation steps + HSTS verify.

## Exercise 6: Image Fix (20 min)
Scan finds CVE in base; bump tag, rebuild, rescan green, sign artifact. Record SBOM diff.

## Exercise 7: WAF Block (15 min)
Write rule blocking IOC path/rate; test legit passes, attack 403s; include expiry review date.

## Exercise 8: Forensic Snapshot (15 min)
Snapshot disk/image + export immutable logs with hashes; chain-of-custody note.

## Exercise 9: Notify Draft (15 min)
Write customer/regulator notice: what, who, window, mitigation, next — no speculation.

## Exercise 10: Post-Mortem (15 min)
5-Whys to static secret + broad RBAC + unpatched image. 3 actions with owners.
