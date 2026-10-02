# Cryptography Deep — Quiz

**10 Questions with Answers & Threat-Model Reasoning**

---

### Q1: Why is ECB mode insecure for encrypting structured data, and what threat does it enable?

**Answer**: ECB encrypts each block independently, so identical plaintext blocks produce identical ciphertext blocks. This leaks patterns in the data.

**Threat-Model Reasoning**: An attacker with ciphertext-only access can infer structure (e.g., repeating headers, image patterns, database records). In a chosen-plaintext scenario, they can build a codebook mapping known plaintexts to ciphertexts, enabling plaintext recovery without the key. This violates IND-CPA security.

---

### Q2: What happens if a nonce is reused with the same key in AES-GCM, and why is this catastrophic?

**Answer**: Reusing a nonce in GCM allows an attacker to compute the XOR of two plaintexts, then recover the authentication key (GHASH key), enabling forgery of arbitrary ciphertexts and full plaintext recovery.

**Threat-Model Reasoning**: GCM's security reduces to a polynomial evaluation over GF(2^128). With two ciphertexts under the same (key, nonce), the attacker solves for the hash key H = C1 ⊕ C2 / (P1 ⊕ P2). Once H is known, they can forge valid tags for any ciphertext (INT-CTXT break) and decrypt messages (IND-CPA break). This is a *total* cryptosystem failure.

---

### Q3: Why must RSA encryption always use padding (OAEP or PKCS#1 v1.5), and what attack does textbook RSA enable?

**Answer**: Textbook RSA (m^e mod n) is deterministic and malleable: an attacker can multiply ciphertexts to produce a valid encryption of the product of plaintexts, or use chosen-ciphertext attacks (Bleichenbacher) to decrypt arbitrary ciphertexts.

**Threat-Model Reasoning**: Without padding, RSA provides no semantic security (IND-CPA). An attacker observing a ciphertext can test guesses by encrypting candidates. With padding oracle access (e.g., server returns "padding error" vs "decryption error"), Bleichenbacher's attack decrypts ciphertexts in ~1M queries. OAEP adds randomness and a redundancy check, providing IND-CCA2 security in the random oracle model.

---

### Q4: In Diffie-Hellman, why must the prime *p* be a safe prime (p = 2q + 1 where q is also prime), and what attack does a non-safe prime enable?

**Answer**: A safe prime ensures the multiplicative group has a large prime-order subgroup, preventing small-subgroup confinement attacks where an attacker forces the shared secret into a small subgroup and brute-forces it.

**Threat-Model Reasoning**: If p-1 has small factors, an attacker can send a public value g^a that lies in a small subgroup. The victim computes (g^a)^b, which is confined to that small subgroup. The attacker then brute-forces the shared secret (at most |subgroup| possibilities). Safe primes and validating that g^a ∈ [2, p-2] with (g^a)^q ≠ 1 mod p prevent this.

---

### Q5: What is the security implication of using a static (long-term) Diffie-Hellman key pair instead of ephemeral keys?

**Answer**: Static DH lacks forward secrecy. If the long-term private key is compromised, *all* past session keys derived from it can be retroactively computed.

**Threat-Model Reasoning**: In a threat model where the server is compromised at time T (e.g., via memory dump, backup theft, or legal seizure), an attacker with recorded past traffic can decrypt all historical sessions if static DH was used. Ephemeral DH (DHE/ECDHE) generates fresh keys per session; compromising one session key does not affect others. Forward secrecy is a critical property for long-term confidentiality.

---

### Q6: Why is ECDSA vulnerable to nonce reuse or biased nonces, and how does this lead to private key recovery?

**Answer**: ECDSA signatures are (r, s) where s = k^(-1)(H(m) + r·d) mod n. If the same nonce *k* is used for two messages, or if *k* is predictable (e.g., biased RNG), the private key *d* can be solved algebraically.

**Threat-Model Reasoning**: With two signatures (r, s1) and (r, s2) using same k: s1 - s2 = k^(-1)(H(m1) - H(m2)) → k = (H(m1) - H(m2)) / (s1 - s2). Then d = (s·k - H(m)) / r. Real-world failures: Sony PS3 (static k), Bitcoin Android wallets (biased RNG), Nintendo Switch (nonce reuse). Deterministic ECDSA (RFC 6979) derives k from the message and private key, eliminating RNG dependence.

---

### Q7: What is the difference between encryption and authentication, and why is "encrypt-then-MAC" the only composition that provides authenticated encryption?

**Answer**: Encryption provides confidentiality; authentication provides integrity. Encrypt-then-MAC computes MAC(ciphertext), ensuring the ciphertext cannot be modified without detection. MAC-then-encrypt and encrypt-and-MAC are vulnerable to padding oracle and other attacks.

**Threat-Model Reasoning**: In MAC-then-encrypt (TLS 1.2), the receiver must decrypt before verifying MAC. A padding oracle in decryption leaks plaintext info (Vaudenay, Lucky13). In encrypt-and-MAC (SSH), MAC is over plaintext; if encryption is malleable, attacker modifies ciphertext and MAC verifies a different plaintext. Encrypt-then-MAC (TLS 1.3, GCM, ChaCha20-Poly1305) verifies MAC *before* decryption; invalid ciphertexts are rejected immediately, eliminating padding oracles.

---

### Q8: Why are small RSA exponents (e=3) dangerous with low-entropy messages or when the same message is sent to multiple recipients?

**Answer**: With e=3, if the same message m is encrypted to 3 recipients with different moduli (n1, n2, n3), an attacker uses the Chinese Remainder Theorem to compute m^3 mod (n1·n2·n3) and takes the integer cube root to recover m. Low-entropy messages allow brute-force by encrypting guesses.

**Threat-Model Reasoning**: Håstad's broadcast attack applies when a message is sent to ≥ e recipients without per-recipient randomness. OAEP padding prevents this by adding random salt per encryption. Using e=65537 is standard; it's large enough to avoid small-exponent attacks while still efficient for verification.

---

### Q9: What is a side-channel attack on AES, and how do constant-time implementations mitigate it?

**Answer**: Side-channel attacks exploit timing, cache access patterns, power consumption, or electromagnetic emanations to extract secret keys. Table-based AES implementations (T-tables) have data-dependent memory accesses, leaking key bits via cache-timing attacks (Bernstein, Osvik-Shamir-Tromer).

**Threat-Model Reasoning**: In a shared-hosting or cloud environment, a co-located attacker can measure cache timing (Flush+Reload, Prime+Probe) to recover AES keys in minutes. Constant-time implementations use bitslicing or hardware AES-NI instructions that execute in fixed time regardless of data. This is essential for any cryptographic code running in multi-tenant environments.

---

### Q10: Explain the difference between IND-CPA, IND-CCA1, and IND-CCA2 security. Which does AES-GCM provide, and why?

**Answer**: 
- **IND-CPA**: Indistinguishability under chosen-plaintext attack (adversary can encrypt chosen plaintexts).
- **IND-CCA1**: Indistinguishability under non-adaptive chosen-ciphertext attack (adversary gets decryption oracle *before* challenge).
- **IND-CCA2**: Indistinguishability under adaptive chosen-ciphertext attack (adversary gets decryption oracle *before and after* challenge, except challenge ciphertext).

AES-GCM provides **IND-CCA2** (authenticated encryption) because the authentication tag binds ciphertext integrity; any modification is detected and rejected before decryption, so the decryption oracle provides no useful information to the attacker.

**Threat-Model Reasoning**: IND-CCA2 models real-world scenarios where attackers can submit crafted ciphertexts (e.g., via API endpoints, network protocols) and observe behavior (error messages, timing). Without authentication (e.g., AES-CBC without MAC), an attacker can manipulate ciphertexts and learn plaintext structure via padding oracles, achieving full decryption. AEAD modes like GCM are the standard for IND-CCA2.