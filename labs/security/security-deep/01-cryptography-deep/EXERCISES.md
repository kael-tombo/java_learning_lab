# Cryptography Deep — Hands-On Exercises

**Hardening & Debugging Tasks** — Each exercise includes a vulnerable/broken implementation to fix, a debugging challenge, or a threat-modeling scenario.

---

## Exercise 1: Fix the ECB Mode Vulnerability

**File**: `src/main/java/com/security/deep/lab01/EcbVulnerability.java`

**Scenario**: A legacy system encrypts user PII (JSON records) using AES-ECB. An attacker with database access can identify which users have the same medical condition by comparing ciphertext blocks.

**Task**:
1. Run the vulnerable code and observe identical ciphertext blocks for identical plaintext fields
2. Refactor to use AES-GCM with proper nonce handling
3. Verify that identical plaintexts now produce different ciphertexts
4. Add authentication tag verification on decryption

**Threat Model**: Attacker has read access to ciphertext database (no key). Goal: prevent pattern leakage.

**Verification**:
```bash
# Before fix: identical 16-byte blocks in ciphertext
# After fix: no identical blocks, authentication tag verified
```

---

## Exercise 2: Nonce Reuse Catastrophe in GCM

**File**: `src/main/java/com/security/deep/lab01/NonceReuseDemo.java`

**Scenario**: A developer uses a counter as GCM nonce but restarts the counter on service restart. Two messages encrypted with same (key, nonce).

**Task**:
1. Run the demo to see two ciphertexts with same nonce
2. Implement the attack: recover GHASH key H = (C1 ⊕ C2) / (P1 ⊕ P2) in GF(2^128)
3. Forge a valid tag for a chosen ciphertext
4. Fix: use 96-bit random nonce (or XChaCha20-Poly1305 with 192-bit nonce)

**Threat Model**: Attacker observes two ciphertexts under same (key, nonce). Goal: demonstrate total break.

**Verification**: Your forge must pass `cipher.verifyTag()`.

---

## Exercise 3: Bleichenbacher Padding Oracle Attack

**File**: `src/main/java/com/security/deep/lab01/BleichenbacherOracle.java`

**Scenario**: A server decrypts RSA-PKCS#1 v1.5 ciphertexts and returns different error codes for "invalid padding" vs "valid padding but wrong content".

**Task**:
1. Implement the padding oracle: `boolean hasValidPadding(byte[] ciphertext)`
2. Implement Bleichenbacher's attack to decrypt a target ciphertext without the private key
3. Fix: use RSA-OAEP, or implement constant-time error handling (always same error message/timing)

**Threat Model**: Attacker can submit arbitrary ciphertexts and observe error behavior. Goal: decrypt one target ciphertext.

**Verification**: Recover the original plaintext in < 2M oracle queries.

---

## Exercise 4: Small Subgroup Confinement in Diffie-Hellman

**File**: `src/main/java/com/security/deep/lab01/SmallSubgroupAttack.java`

**Scenario**: A DH implementation uses a 1024-bit prime where p-1 has small factors. No validation of peer's public value.

**Task**:
1. Find a small subgroup generator g' where g'^q = 1 mod p for small q
2. Send g' as your public value; victim computes (g')^b
3. Brute-force the shared secret (at most q possibilities)
4. Fix: validate peer public value ∈ [2, p-2] and (g^a)^q ≠ 1 mod p

**Threat Model**: Active attacker controls network, can send arbitrary public values. Goal: recover session key.

**Verification**: Your attack recovers the shared secret in < 1000 operations.

---

## Exercise 5: ECDSA Nonce Reuse Private Key Recovery

**File**: `src/main/java/com/security/deep/lab01/EcdsaNonceReuse.java`

**Scenario**: A signing service uses a broken RNG that occasionally repeats nonces.

**Task**:
1. Generate two signatures (r, s1) and (r, s2) with same r (same nonce k)
2. Implement the algebraic key recovery: k = (H(m1) - H(m2)) / (s1 - s2), then d = (s·k - H(m)) / r
3. Fix: implement RFC 6979 deterministic ECDSA (k = HMAC(d || m))

**Threat Model**: Attacker observes two signatures with same r. Goal: recover private signing key.

**Verification**: Recovered private key must verify against the public key.

---

## Exercise 6: MAC-then-Encrypt Padding Oracle (Lucky13 Style)

**File**: `src/main/java/com/security/deep/lab01/MacThenEncryptOracle.java`

**Scenario**: A protocol uses AES-CBC + HMAC-SHA256 in MAC-then-encrypt order. Decryption checks padding before MAC.

**Task**:
1. Implement the padding oracle: distinguish "padding error" (fast return) from "MAC error" (slow return)
2. Decrypt a target ciphertext block-by-block using the oracle
3. Fix: switch to encrypt-then-MAC (compute HMAC over ciphertext, verify before decryption)

**Threat Model**: Attacker submits ciphertexts, measures response time. Goal: decrypt without key.

**Verification**: Recover full plaintext using timing side-channel only.

---

## Exercise 7: Håstad's Broadcast Attack on RSA-e=3

**File**: `src/main/java/com/security/deep/lab01/HastadBroadcast.java`

**Scenario**: Same message encrypted to 3 recipients with e=3, different moduli, no per-recipient randomness.

**Task**:
1. Encrypt message m to three recipients: c1 = m^3 mod n1, c2 = m^3 mod n2, c3 = m^3 mod n3
2. Use Chinese Remainder Theorem to compute c = m^3 mod (n1·n2·n3)
3. Compute integer cube root of c to recover m
4. Fix: use OAEP padding (adds randomness per encryption) or e=65537

**Threat Model**: Attacker intercepts 3 ciphertexts of same message. Goal: recover message without any private key.

**Verification**: Recovered m matches original exactly.

---

## Exercise 8: Cache-Timing Attack on T-Table AES

**File**: `src/main/java/com/security/deep/lab01/CacheTimingAes.java`

**Scenario**: An AES implementation uses T-tables (precomputed S-box + MixColumns tables). In a shared cloud environment, a co-located attacker runs Flush+Reload.

**Task**:
1. Implement T-table AES with observable cache access pattern
2. Write a spy thread that flushes cache lines and measures reload time
3. Correlate cache hits with key-dependent table indices to recover key bytes
4. Fix: use AES-NI intrinsics (constant-time) or bitsliced implementation

**Threat Model**: Attacker shares physical CPU, can measure cache timing. Goal: extract AES key.

**Verification**: Recover at least 8 key bytes with >90% accuracy in < 100K encryptions.

---

## Exercise 9: Forward Secrecy Violation — Static DH Compromise

**File**: `src/main/java/com/security/deep/lab01/StaticDhCompromise.java`

**Scenario**: A messaging app uses static DH key pairs (identity keys) for all sessions. No ephemeral keys.

**Task**:
1. Simulate 100 sessions with static DH, record all ciphertexts
2. "Compromise" the server: extract the long-term private key
3. Retroactively decrypt all 100 recorded sessions
4. Fix: implement X25519 ephemeral DH per session (Signal-style double ratchet optional)

**Threat Model**: Passive recorder captures traffic. Later, server key is leaked. Goal: decrypt history.

**Verification**: All 100 historical messages decrypted after key compromise.

---

## Exercise 10: Design a Threat Model for a Crypto Library

**File**: `docs/threat-model-crypto.md` (create this)

**Scenario**: You're building a Java crypto library for internal teams. Define the threat model.

**Task**:
1. Identify assets: keys, plaintexts, randomness, API correctness
2. Identify adversaries: malicious caller, co-tenant in cloud, compromised dependency, side-channel observer
3. Define trust boundaries: library vs application, JVM vs OS, CPU cache
4. For each crypto primitive (AES-GCM, RSA-OAEP, X25519, Ed25519, HKDF, Argon2id):
   - What security property does it provide? (IND-CCA2, EUF-CMA, etc.)
   - What implementation pitfalls break it?
   - What mitigations does your library enforce?
5. Document: key lifecycle (generation, storage, rotation, destruction), RNG requirements, constant-time guarantees

**Deliverable**: A `THREAT_MODEL.md` file with:
- Asset table
- Adversary capabilities table  
- Per-primitive security claims + assumptions
- Required mitigations checklist
- Testing/validation requirements (Wycheproof vectors, side-channel testing)

---

## Running the Exercises

```bash
cd labs/security/security-deep/01-cryptography-deep
./gradlew test --tests "*Exercise*"
```

Each exercise has a corresponding test in `src/test/java/com/security/deep/lab01/` that verifies:
- The vulnerability exists in the starter code
- Your fix resolves it
- The threat model is correctly addressed