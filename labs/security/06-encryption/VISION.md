# VISION — Encryption: Modes, Nonces, and Key Lifecycle
> Where this lab takes you: from "call AES and I'm done" to choosing a mode, an IV strategy, and a rotation plan you can defend.

## The Arc
1. **Primitives** — block ciphers, stream ciphers, hashes, MACs, and what each actually guarantees.
2. **Modes matter** — ECB leaks structure; CBC needs unpredictable IVs; GCM needs a unique nonce.
3. **Asymmetric** — key agreement (ECDH), signatures (ECDSA/Ed25519), and hybrid encryption.
4. **Key management** — generation, storage, wrapping/unwrapping (KEK/DEK), rotation, escrow.
5. **Application crypto** — password hashing, at-rest field encryption, envelope encryption, HSMs.

## Milestones (checkable)
- [ ] M1: encrypt the same plaintext with ECB and AES-GCM and show the ECB pattern leaking.
- [ ] M2: state the IV/nonce requirements for CBC and GCM and what happens when violated.
- [ ] M3: implement authenticated decryption and reject a single flipped ciphertext bit.
- [ ] M4: build a hybrid scheme (ECDH + HKDF + AES-GCM) and explain each component's role.
- [ ] M5: design a KEK/DEK rotation where re-wrapping never requires decrypting bulk data.

## Core Competencies
- Mode selection driven by integrity requirements, not speed benchmarks.
- Nonce/IV generation discipline and the catastrophic failure modes of reuse.
- Envelope encryption: data key wrapped by a key-encrypting key, re-wrapped on rotation.
- Constant-time comparison and why `equals` on MACs is a vulnerability.
- Java CryptoArchitecture pitfalls: provider defaults, ECB mode defaults, `PBEKeySpec` clearing.

## Anti-Goals
- Inventing a cipher mode, a key derivation, or a "custom crypto" format.
- Rolling your own crypto instead of using JCE, Bouncy Castle, or a KMS.
- Storing raw key bytes in config, source, or a database column.

## Interview Lens
- "Why is ECB forbidden for images?" "How do you rotate a data key without re-encrypting the table?"
- "Your GCM IV is a random 12 bytes. Is that wrong? Argue both sides."

## 30-Day Plan
- Wk1 THEORY + EXERCISES: break ECB, forge a CBC padding error, flip a GCM bit.
- Wk2 QUIZ/FLASHCARDS to 90%+; implement AES-GCM and ECDSA by hand.
- Wk3 MINI_PROJECT with envelope encryption and re-wrapping.
- Wk4 REAL_WORLD_PROJECT: field-level encryption for a regulated datastore.

## Done = You Can
- Choose a mode and nonce strategy, defend it in a design review, and implement
  key rotation that never requires bulk re-encryption or plaintext on disk.
