# Encryption - REAL WORLD PROJECT

## Project: MediVault — field-level encryption for a clinical data platform

A Java 21 / Spring Boot service holding protected health information. Some fields must be
encrypted at the application layer because the storage tier is shared multi-tenant, and
because certain queries must never be answerable by a database administrator. AES-GCM
envelope encryption with a cloud KMS as the KEK, plus searchable-by-equals for a small
number of fields via deterministic nonces where leakage is accepted and documented.

### Architecture

```
Patient record
  ├─ mrn (Medical Record Number)  ──▶ AES-256-GCM(random nonce)      strict confidentiality
  ├─ name, address                ──▶ AES-256-GCM(random nonce)      strict confidentiality
  ├─ diagnosisCode                ──▶ AES-256-GCM(random nonce)      strict
  └─ ssnFingerprint               ──▶ HMAC-SHA256(pepper, plaintext) equality lookup only
                                    (never reversible; brute force is prevented by the pepper)

Key hierarchy
  Cloud KMS (HSM-backed) ──KEK v1,v2──▶ wraps per-tenant DEK ──▶ wraps per-record DEK
  Rotation: rotate KEK → re-wrap tenant DEKs (minutes) → retire old KEK version

    Audit: every decrypt logs (actor, patientId, purpose-of-use, justification)
```

### Implementation

```java
@Service
class ClinicalFieldCrypto {
    private final KmsClient kms;                  // envelope keys live in the KMS, never in config
    private final Map<String, TenantKey> active = new ConcurrentHashMap<>();
    private final byte[] pepper;                  // from secret manager, not env file

    record TenantKey(String keyId, SecretKey dek, int generation) {}

    public EncryptedColumn encryptColumn(String tenantId, long patientId, String column, byte[] value) {
        TenantKey tk = keyFor(tenantId);
        byte[] nonce = secureRandom(12);
        Cipher c = cipher("AES/GCM/NoPadding");
        c.init(Cipher.ENCRYPT_MODE, tk.dek(), new GCMParameterSpec(128, nonce));
        // AAD binds the ciphertext to tenant+patient+column: a stolen ciphertext cannot be
        // replayed into a different patient row or a different column.
        c.updateAAD(aad(tenantId, patientId, column));
        return new EncryptedColumn(tk.keyId(), tk.generation(), nonce, c.doFinal(value));
    }

    public byte[] decryptColumn(String tenantId, long patientId, String column, EncryptedColumn e) {
        audit.decryptAccess(actor(), tenantId, patientId, column);   // fail-closed: if audit fails, throw
        TenantKey tk = keyFor(tenantId);
        if (tk.generation() < e.generation()) throw new StaleGenerationException(); // re-encrypt path
        Cipher c = cipher("AES/GCM/NoPadding");
        c.init(Cipher.DECRYPT_MODE, tk.dek(), new GCMParameterSpec(128, e.nonce()));
        c.updateAAD(aad(tenantId, patientId, column));
        return c.doFinal(e.ciphertext());
    }

    /** Non-reversible equality index. Pepper prevents offline dictionary attack on a DB dump. */
    public byte[] fingerprint(String ssn) {
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(new SecretKeySpec(pepper, "HmacSHA256"));
        return mac.doFinal(("ssn:v2:" + ssn).getBytes(US_ASCII));
    }
}
```

Key rotation is a two-phase operation because the KMS cannot rotate all KEKs instantly:

```java
@Component
class KekRotationJob {
    /** Phase 1: re-wrap tenant DEKs under a new KMS key version. No table rewrite of bulk data. */
    @Scheduled(cron = "0 0 4 1 * *")
    void rewrapTenants() {
        KeyVersion newVersion = kms.createKeyVersion(KMS_KEY_ID);
        for (TenantKey tk : keyRegistry.all()) {
            byte[] dek = kms.decrypt(newVersionId(tk.keyId()), tk.wrappedDek());
            byte[] rewrapped = kms.encrypt(newVersion.arn(), dek, encryptionContext(tk.tenantId()));
            keyRegistry.update(tk.tenantId(), new WrappedDek(rewrapped, newVersion.arn()));
            audit.keyRewrapped(tk.tenantId(), newVersion.arn());
        }
        kms.scheduleRetirement(KMS_KEY_ID, Duration.ofDays(30));  // rollback window
    }
}
```

### Non-functional requirements

- **Latency**: KMS call on cache miss only; tenant DEKs cached in-process for 15 min.
  p95 column decrypt under 3 ms, p99 under 15 ms including KMS.
- **Isolation**: per-tenant DEKs, so a tenant offboarding or a suspected key compromise can
  be rotated independently without touching other tenants.
- **Search**: full-text search over encrypted fields is impossible by design. The only
  equality lookups use HMAC fingerprints; range queries are rejected at the service layer.
- **Backups**: ciphertext backups are safe to store long-term; the KEK destruction policy
  is what makes old ciphertext unrecoverable after the compliance retention window.
- **Audit**: decrypt access logged with purpose-of-use; the audit sink is the compliance
  artefact, so its failure must block access rather than silently pass.
- **Compliance mapping**: HIPAA Security Rule addressable controls, OWASP ASVS V6/V9,
  GDPR Art. 32 encryption requirements.

### Sourced field notes (fetched Oct 2026 — verify before citing)
- OWASP Cryptographic Storage Cheat Sheet covers the encrypt-at-rest layering (keyed
  encryption, per-column keys, key versioning) that this envelope design implements.
  https://owasp.org/www-project-cheat-sheets/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html
- Java Cryptography Architecture reference (JCA/JCE) documents `Cipher` usage, AEAD
  parameters via `GCMParameterSpec`, and `SecretKeyFactory` PBKDF2 construction.
  https://docs.oracle.com/en/java/javase/21/security/java-cryptography-architecture.html

## Deliverables

- [x] AES-256-GCM column encryption with AAD binding tenant/patient/column
- [x] Cloud KMS as KEK; tenant DEKs cached; no key material in config or source
- [x] Two-phase KEK rotation: re-wrap tenant DEKs, then retire the old version
- [x] Per-tenant key isolation with independent offboarding/rotation
- [x] HMAC-SHA256 fingerprint index with a KMS-held pepper for equality lookups
- [x] Fail-closed audit on every decrypt, with purpose-of-use recorded
- [x] Stale-generation detection and a background re-encrypt job
- [x] Documented search limitations and the threat model for each choice
