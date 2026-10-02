# Cryptography Deep — Flashcards

---

## Symmetric Encryption

**Q: What is the key difference between symmetric and asymmetric encryption?**
**A:** Symmetric uses the same key for encrypt/decrypt (AES); asymmetric uses a public/private key pair (RSA). Symmetric is fast but has key distribution problem; asymmetric is slower but solves key distribution.

---

**Q: Name three AES modes and their security properties.**
**A:** 
- ECB: Insecure, deterministic, leaks patterns
- CBC: Semantically secure with random IV, malleable without MAC
- GCM: Authenticated encryption (AEAD), provides confidentiality + integrity

---

**Q: Why must you never reuse a (key, nonce) pair in AES-GCM?**
**A:** Nonce reuse allows recovery of the GHASH authentication key, enabling ciphertext forgery and full plaintext recovery. It breaks both confidentiality and integrity completely.

---

**Q: What is the minimum recommended AES key size today?**
**A:** 128 bits (AES-128). AES-256 for long-term secrets or compliance. Never use keys < 128 bits.

---

**Q: How should IVs be generated for CBC mode?**
**A:** Cryptographically random (SecureRandom), unique per encryption, unpredictable. Never use a fixed or counter IV.

---

## Asymmetric Encryption

**Q: What is the RSA key generation process?**
**A:** 1) Choose large primes p, q. 2) n = p·q. 3) φ(n) = (p-1)(q-1). 4) Choose e (typically 65537) with gcd(e, φ(n)) = 1. 5) Compute d = e^(-1) mod φ(n). Public key = (n, e); private key = (n, d).

---

**Q: Why is textbook RSA (m^e mod n) insecure?**
**A:** Deterministic (no semantic security), malleable (c1·c2 = (m1·m2)^e), vulnerable to chosen-ciphertext attacks (Bleichenbacher). Always use OAEP padding.

---

**Q: What is RSA-OAEP and why is it secure?**
**A:** Optimal Asymmetric Encryption Padding. Adds random seed, uses mask generation function (MGF1). Provides IND-CCA2 in random oracle model. Prevents Bleichenbacher and broadcast attacks.

---

**Q: What is the minimum RSA key size today?**
**A:** 2048 bits. 3072+ for long-term. 1024-bit is broken.

---

**Q: What is the Bleichenbacher attack?**
**A:** Padding oracle attack on PKCS#1 v1.5. Server leaks "valid padding" vs "invalid padding" → attacker decrypts ciphertext in ~1M queries. Mitigation: use OAEP, or constant-time error handling.

---

## Key Exchange

**Q: How does Diffie-Hellman key exchange work?**
**A:** Public params: prime p, generator g. Alice picks a, sends g^a mod p. Bob picks b, sends g^b mod p. Shared secret: g^(ab) mod p. Attacker sees g^a, g^b but cannot compute g^(ab) (discrete log problem).

---

**Q: What is a safe prime and why does DH need one?**
**A:** p = 2q + 1 where q is prime. Ensures large prime-order subgroup. Prevents small-subgroup confinement attacks where attacker forces shared secret into small subgroup and brute-forces it.

---

**Q: What is forward secrecy and how does DHE/ECDHE achieve it?**
**A:** Compromise of long-term keys doesn't reveal past session keys. DHE generates fresh ephemeral DH keys per session. Session keys are derived from ephemeral keys, then discarded.

---

**Q: What is the Logjam attack?**
**A:** Precomputation attack on DH using common 1024-bit primes. Nation-state can break one prime and decrypt all connections using it. Mitigation: use 2048+ bit primes, or ECDHE (no precomputation).

---

**Q: What is ECDH?**
**A:** Elliptic Curve Diffie-Hellman. Same protocol but over elliptic curve group. Smaller keys (256-bit ≈ 3072-bit RSA), faster, no precomputation attacks.

---

## Elliptic Curve Cryptography

**Q: What is the elliptic curve discrete logarithm problem (ECDLP)?**
**A:** Given P = k·G (scalar multiplication), find k. Believed exponentially harder than integer factorization or finite-field DLP for same key size.

---

**Q: What curves are recommended for ECC?**
**A:** NIST P-256, P-384, P-521; Curve25519 (X25519 for DH, Ed25519 for signatures). Avoid custom curves.

---

**Q: What is the cofactor in ECC and why does it matter?**
**A:** h = #E(F_p) / n (curve order / subgroup order). Small cofactor (h=1, 4, 8) is good. Large cofactor enables small-subgroup attacks. Validate points are in correct subgroup.

---

## Digital Signatures

**Q: How does RSA signing work?**
**A:** Sign: s = H(m)^d mod n. Verify: s^e mod n = H(m). Uses padding (PSS or PKCS#1 v1.5). PSS is probabilistic and has security reduction.

---

**Q: What is the ECDSA signing equation?**
**A:** Pick random k. r = x(k·G) mod n. s = k^(-1)(H(m) + r·d) mod n. Signature = (r, s). Verify: u1 = H(m)·s^(-1), u2 = r·s^(-1), check x(u1·G + u2·Q) = r.

---

**Q: Why is nonce reuse in ECDSA catastrophic?**
**A:** Two signatures with same k give: s1 - s2 = k^(-1)(H(m1) - H(m2)). Solve for k, then compute private key d = (s·k - H(m))/r mod n. Private key fully recovered.

---

**Q: What is RFC 6979 (Deterministic ECDSA)?**
**A:** Derives k = HMAC(private_key || message) instead of random. Eliminates RNG failures. Used in Bitcoin, Ethereum, modern TLS libraries.

---

**Q: What is EdDSA / Ed25519?**
**A:** Deterministic Schnorr signatures on Curve25519. No RNG needed, faster, side-channel resistant, no nonce reuse risk. Preferred over ECDSA.

---

## Hash Functions & MACs

**Q: What properties must a cryptographic hash have?**
**A:** Preimage resistance, second preimage resistance, collision resistance. SHA-256, SHA-3, BLAKE2/3 are standard. MD5, SHA-1 are broken.

---

**Q: What is HMAC and why not just H(k || m)?**
**A:** HMAC(k, m) = H((k ⊕ opad) || H((k ⊕ ipad) || m)). Prevents length-extension attacks. H(k || m) is vulnerable if H is Merkle-Damgård (SHA-256, SHA-1).

---

**Q: What is a length-extension attack?**
**A:** Given H(m) and len(m), attacker can compute H(m || pad || m') without knowing m. SHA-256, SHA-1 vulnerable. SHA-3, BLAKE2, HMAC are not.

---

## Key Derivation

**Q: What is PBKDF2 / Argon2 / scrypt?**
**A:** Password-based key derivation functions. Add salt + iteration count (PBKDF2), memory hardness (scrypt, Argon2) to slow GPU/ASIC brute-force. Argon2id is current recommendation.

---

**Q: What is HKDF and when to use it?**
**A:** HMAC-based Key Derivation Function. Two steps: Extract (salt + IKM → PRK), Expand (PRK + info → OKM). Use to derive multiple keys from a master secret (e.g., TLS key schedule).

---

## Threat Modeling Flashcards

**Q: What threat does ECB mode enable?**
**A:** Pattern leakage → ciphertext-only pattern analysis, codebook attacks under chosen-plaintext.

---

**Q: What threat does nonce reuse in GCM enable?**
**A:** Total break: authentication key recovery → ciphertext forgery (INT-CTXT) + plaintext recovery (IND-CPA).

---

**Q: What threat does missing padding in RSA enable?**
**A:** Chosen-ciphertext attack (Bleichenbacher) → full decryption oracle.

---

**Q: What threat does static DH enable?**
**A:** No forward secrecy → retroactive decryption of all past sessions if long-term key compromised.

---

**Q: What threat does ECDSA nonce reuse enable?**
**A:** Private key recovery via algebraic solution → total compromise of all signatures past and future.

---

**Q: What threat does MAC-then-encrypt enable?**
**A:** Padding oracle attacks (Lucky13, Vaudenay) → plaintext recovery via decryption error side-channel.

---

**Q: What threat does small RSA exponent (e=3) with broadcast enable?**
**A:** Håstad's attack → CRT + integer root → plaintext recovery without private key.

---

**Q: What threat does non-constant-time AES enable?**
**A:** Cache-timing side-channel (Flush+Reload) → key extraction in shared environments.

---

**Q: What threat does missing forward secrecy enable?**
**A:** Retroactive decryption of recorded traffic upon long-term key compromise (legal seizure, backup theft, memory dump).

---

**Q: What threat does unauthenticated encryption enable?**
**A:** Ciphertext malleability → bit-flipping attacks, padding oracles, IND-CCA2 break.