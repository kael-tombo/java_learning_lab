# Lab 09: Security Engineering in Production — Math Foundation

Security decisions have quantitative consequences: how long a leaked credential stays useful, how big a blast radius a key has, how much entropy you need, how expensive hashing and encryption are in latency. These are the numbers.

---

## 1. Credential lifetime and blast radius

```
blast_radius_window ≈ token_ttl × number_of_instances_that_can_use_it
effective_exposure  = compromised_at_time + ttl
```

Static DB password with manual rotation every 90 days:
```
exposure_window = 90 days = 7,776,000 s
```

OIDC access token, 15-minute TTL:
```
exposure_window = 15 min = 900 s   →  518× smaller
revocation_without_state = impossible; with a denylist, seconds
```

**Conclusion**: prefer short-lived, dynamically issued credentials. Rotating frequency is a direct multiplier on worst-case damage, and TTL is the only number that shrinks it without an operational process.

---

## 2. Password hashing cost

```
hash_time_ms = cost_setting × calibration
memory_hardness: Argon2id m (KiB), t iterations, p lanes
bcrypt: 2^cost iterations
```

Cost calibration goal: **250–1000 ms per hash on your production hardware**, so an attacker with the same hardware gains nothing from parallel guessing beyond your login rate limit allows.

If your hardware is 4× faster than when you set `cost=10`:
```
safe_cost = log2(10) + log2(4) = 3.32 + 2 = 5.32 → cost 13
```
bcrypt cost 13 = 8× the work of cost 10 → ~8× hash time. Measure, do not guess; record the calibration benchmark in the repo.

Password-cracking economics:
```
attempts_needed = 2^(entropy_bits)
attempts_per_hour = attacker_guesses_per_second × 3600
time_to_crack = 2^entropy / guesses_per_second
```

A 4-character lowercase password = ~23 bits:
```
time = 2^23 / (10^10 guesses/s) ≈ 0.001 s     →  instant
```
A 16-character passphrase = ~100 bits:
```
time = 2^100 / 10^10 s ≈ 4 × 10^20 s  →  age of the universe, ×13
```
**Conclusion**: length beats character-class rules, always enforce a minimum of ~12–16 characters, and block the top leaked-password list — the math says composition rules do almost nothing.

---

## 3. Brute-force and credential-stuffing exposure

```
online_guesses_possible = login_rate_limit × ttl
effective_rate = attempts / (account_count × ttl)      distributed attacks
```

Rate limit 5/min, 24 h TTL, 1M accounts:
```
per-account per day = 5 × 1440 = 7,200 guesses
fleet-wide = 7,200 × 1,000,000 = 7.2 × 10^9 attempts/day
```

Add per-account lockout/backoff and device fingerprinting: attempts drop by 2–3 orders of magnitude for the same attacker effort. Also weight by IP reputation — credential stuffing is inherently many-accounts-per-source, which is a detectable signal.

**Conclusion**: the control that matters is not the password policy but the per-identity attempt budget plus MFA, which reduces the useful guess rate to ~0 for phished credentials.

---

## 4. TLS handshake and mTLS cost

```
handshake_cpu_ms ≈ RSA2048_verify(0.1 ms) + ECDHE(0.3 ms) + [client_cert_verify: +0.5–2 ms]
tls13_1rtt_latency ≈ 1 RTT for resumed, 1 RTT + 0.5–1 ms crypto for full
```

At 5,000 rps with per-request connections (a bug) and 1 ms crypto:
```
handshakes/s = 5,000   →  5,000 × 1 ms = 5 CPU-seconds/s  →  5 cores burned on crypto alone
```

With connection reuse (100 requests per connection):
```
handshakes/s = 5,000 / 100 = 50/s  →  0.05 cores    →  100× reduction
```
**Conclusion**: mTLS is affordable; per-request handshakes are not. Reuse connections and enable session resumption.

---

## 5. JWT size and header cost

```
jwt_bytes ≈ base64url(header) + base64url(payload) + base64url(sig)
RSA2048 sig = 256 B   →  ~342 B header+sig
EC P-256 sig = 64 B   →  ~150 B
```

Payload with 8 claims (~40 chars each):
```
payload ≈ 320 B → base64url ≈ 430 B
total (RSA) ≈ 770 B   total (EC) ≈ 580 B
```

Bandwidth at 5,000 rps inbound + outbound:
```
RSA: 5,000 × 2 × 770 B ≈ 7.7 MB/s  →  ~62 MB/month per service, trivial
```
**Conclusion**: token size is a bandwidth non-issue; the real cost of putting claims in the JWT is *governance* — you cannot revoke a claim without rotating the token, and PII in a decodeable payload is a breach of trust. Keep claims minimal and stable.

---

## 6. Rate-limit and abuse-control arithmetic

```
token_bucket: tokens = min(capacity, tokens + rate × Δt)
429 rate = 1 - min(1, allowed / offered)
```

API quota: 1,000 req/min per tenant, burst 200:
```
steady allowed  = 16.7 req/s per tenant
burst allowance = 200 − 16.7 = 183 immediate   →  a 11.7× instantaneous spike is tolerated
```
Set `capacity = burst` deliberately. If `capacity == rate`, you reject every spike — a retrying client turns a brief overload into a sustained outage.

Global protection: edge rate limit `R_edge`, per-tenant `R_tenant`, service capacity `C`:
```
overload iff Σ_tenants min(R_tenant, demand) > C
```
Use a token bucket at the edge with `R_edge ≤ C / 3` so that abusive single-tenant traffic cannot consume more than a third of capacity — the standard 3× rule of thumb.

---

## 7. Key rotation and encryption blast radius

```
n_keys = rotation_interval / key_lifetime
encrypted_objects_decryptable = objects_whose_key_is_still_valid
```

Envelope encryption with a data key per object and a KEK rotated every 90 days:
```
objects with decryptable key = 90 days of writes
a leaked KEK decrypts = 90 days of data   →  bounded
a leaked data key decrypts = 1 object      →  tiny
```
Contrast with a single application-wide key rotated annually:
```
leaked key decrypts = 1 year of data       →  unacceptable for PII
```
**Conclusion**: encrypt PII with per-object (or per-tenant) data keys under a versioned KEK; rotation becomes a metadata operation, not a re-encryption of the whole table.

---

## 8. Logging and telemetry exposure

```
log_volume_with_pii = requests × P(log body) × body_bytes
pii_in_sinks        = app_logs, APM spans, error trackers, analytics, SIEM, backups
```

`λ = 2,000/s`, 100% logging with a 2 KB JSON body including an authorization header:
```
volume = 2,000 × 2,000 B = 4 MB/s = 345 GB/day
```
If that stream reaches a third-party APM, your retention and access control are now that vendor's problem, and the token in the log is valid until expiry.

Masking budget:
```
masked_fields_per_request = headers(4) + body_pii_fields(6) + query(3)
residual_risk ≈ P(any field you forgot) — measurable only by audit, not by math
```
**Conclusion**: allow-list what you log rather than deny-list what you scrub, and add a CI regex check for `log\..*(password|token|authorization|secret)`.

---

## 9. Availability as a security property

```
effective_downtime = attack_success_time × P(defense_fails)
cost_of_overblocking = false_positive_rate × (manual review time × volume)
```

Add a WAF rule that blocks `SELECT.*UNION`:
```
legitimate traffic matching pattern ≈ 0.05% of 2,000 rps = 1 rps
cost if over-blocked = 1 rps × manual review = ongoing toil
benefit = removes one injection vector (but parameterised queries already did)
```
A WAF is a second layer with a measurable false-positive cost. **Conclusion**: fix the injection at the query layer (zero false positives), then add the WAF as defence in depth with an observed-rate review.

Rate-limit-induced self-DoS:
```
retry_storm_load = offered × (1 + β)     β = retry fraction
with β = 0.5 and a 50% capacity loss: 0.5 × 1.5 = 0.75 of healthy capacity  →  survives
with β = 1.0:                              0.5 × 2.0 = 1.0 of healthy capacity  →  exactly at the edge, oscillates
```
Cap client retries globally at ≤10% of volume.

---

## 10. Audit-log integrity and volume

```
audit_records/day = auth_events + authz_denials + data_exports + config_changes
retention_requirement = regulatory (often 1–7 years)
volume = records × avg_bytes × retention_multiplier
```

1M requests/day, 2% produce an audit-worthy authz decision, 300 B each:
```
200,000 × 300 B = 60 MB/day  →  22 GB/year, compressible to ~4 GB
```
Hash-chain for tamper evidence:
```
chain_hash_n = SHA256(chain_hash_{n-1} || record_n)
verify_cost  = N hashes   →  trivial; makes deletion detectable
```

---

## 11. Authentication cost vs. session cost

```
auth_cost = crypto_ms + network_RTT + policy_eval_ms
session_lookup_cost = cache_hit_ns vs token_verify_ms
```

mTLS + JWT verification per request: `~0.1–0.2 ms` CPU.
Session lookup: `~0.05 µs` on a local cache hit, `~1 ms` on a network Redis round trip.

```
JWT: 0.15 ms/request at 5,000 rps = 0.75 cores
Redis session: 1 ms/network per request → 5 cores + a network dependency
```
JWT wins on cost and removes a shared dependency (a single point of failure). **Conclusion**: short-lived JWTs for services, revocable state only where a hard revocation requirement exists.

---

## 12. Vulnerability remediation economics

```
expected_loss = P(exploit_attempted) × P(successful) × impact
remediation_cost = engineering_days × day_rate × (fraction of the fleet)
```

CVE with a public exploit, KEV-listed:
```
remediation_priority = P(exploited) × impact / (time_to_deploy)
```
Fleet rebuild cost: 14 services × 40 min pipeline = 9.3 hours of CI time. Batch the rebuild into one base-image bump so the marginal cost per service is a re-tag, not a full build.

**Conclusion**: measure your patch latency (`detect → deployed`) as a security SLO. It is the number that determines exposure duration, and it is entirely under your control.

---

## 13. Quick drills

1. Access token TTL 15 min vs static password rotated every 90 days — exposure ratio? **Answer: 7,776,000/900 ≈ 8,640× smaller.**
2. 4-char lowercase password vs 16-char passphrase, attacker at 10^10 guesses/s. **Answer: ~23 bits = instant; ~100 bits = longer than the universe.**
3. bcrypt cost 10 with hardware 4× faster — new cost? **Answer: ~13 (log2(4)=2 more). Measure.**
4. mTLS at 5,000 rps, per-request handshake (1 ms) vs 100 req/connection. **Answer: 5 cores vs 0.05 cores.**
5. Service capacity 3,000 rps, abusive tenant sending 2,000. Edge rate limit should be? **Answer: ≤ C/3 = 1,000 rps so one tenant can't take more than a third.**
6. Kafka: KEK rotated every 90 days, one app-wide key vs per-object data keys — blast radius? **Answer: 90 days of all data vs one object.**
7. 2,000 rps logging 2 KB bodies with an auth header. **Answer: ~345 GB/day, replicated to third parties. Log an allow-list instead.**
8. Retry fraction 1.0 during a 50% capacity loss. **Answer: 0.5×2.0 = 1.0 → oscillates. Cap retries at ≤10%.**

---

## 14. Formulas worth memorizing

| Formula | Use |
|---|---|
| `exposure = ttl` | blast radius of a leaked credential; minimize TTL |
| `time_to_crack = 2^entropy / guesses_per_second` | password policy; length over complexity |
| `hash_cost = log2(cost0) + log2(speedup)` | re-calibrate bcrypt/Argon2 when hardware changes |
| `handshake_cost = rps × crypto_ms × (1/req_per_conn)` | why mTLS needs connection reuse |
| `token_bucket capacity = burst`, not rate | avoid self-DoS from clients |
| `R_edge ≤ C/3` | edge rate limit protecting service capacity |
| `blast_radius = rotation_interval` | envelope encryption with per-object data keys |
| `retry load = offered × (1+β)` | cap β ≤ 10% to survive partial outages |
| `leaked_token_valid_until = ttl` | the number your revocation design must beat |
| `patch_latency = deployed_at − advisory_at` | the security SLO you control |
