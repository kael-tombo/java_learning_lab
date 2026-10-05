# Encryption - MINI PROJECT

## Project: VaultCrypto — an envelope-encryption library with rotation that never decrypts the corpus

Implement a small crypto library: AES-GCM for data keys, ECDH for agreement, HKDF for
derivation, plus KEK/DEK wrapping so a key rotation only re-wraps 1 KB instead of the
whole dataset.

### Architecture

```
Encrypt(plaintext):
   DEK = random 256-bit                       (fresh per record)
   ct, tag = AES-256-GCM(DEK, nonce, plaintext, aad=recordId||version)
   wrappedDEK = AES-256-GCM(KEK, wrapNonce, DEK, aad=keyId||recordId)
   store(keyId, wrapNonce, wrappedDEK, nonce, ct, tag)

Decrypt(row):
   DEK = AES-256-GCM-decrypt(KEK, row.wrapNonce, row.wrappedDEK)  -> un-unlock
   pt = AES-256-GCM-decrypt(DEK, row.nonce, row.ct, row.tag)

Rotate KEK v1 -> v2:
   for each row: DEK = unwrap(KEK_v1, row); rewrap(KEK_v2, DEK)   # ciphertext untouched
   then destroy KEK_v1   # after a safety window for in-flight readers
```

### Implementation

```java
public final class VaultCrypto {
    private static final int DEK_BITS = 256, NONCE_BYTES = 12, TAG_BITS = 128;
    private final Map<String, SecretKey> keks;    // keyId -> active KEK
    private final String activeKeyId;

    public SealedRow seal(long recordId, byte[] plaintext) throws GeneralSecurityException {
        SecretKey dek = generateDataKey();                       // fresh per record
        byte[] nonce = secureRandom(NONCE_BYTES);               // MUST be unique per (key, msg)
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        c.init(ENCRYPT_MODE, dek, new GCMParameterSpec(TAG_BITS, nonce));
        c.updateAAD(aadFor(recordId));                          // binds ciphertext to its row
        byte[] ct = c.doFinal(plaintext);

        byte[] wrapNonce = secureRandom(NONCE_BYTES);
        Cipher w = Cipher.getInstance("AES/GCM/NoPadding");
        w.init(ENCRYPT_MODE, keks.get(activeKeyId), new GCMParameterSpec(TAG_BITS, wrapNonce));
        w.updateAAD(aadForKey(recordId));
        return new SealedRow(activeKeyId, wrapNonce, w.doFinal(dek.getEncoded()), nonce, ct);
    }

    public byte[] open(long recordId, SealedRow row) throws GeneralSecurityException {
        Cipher w = Cipher.getInstance("AES/GCM/NoPadding");
        w.init(DECRYPT_MODE, keks.get(row.keyId()), new GCMParameterSpec(TAG_BITS, row.wrapNonce()));
        w.updateAAD(aadForKey(recordId));
        SecretKey dek = new SecretKeySpec(w.doFinal(row.wrappedDek()), "AES");

        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        c.init(DECRYPT_MODE, dek, new GCMParameterSpec(TAG_BITS, row.nonce()));
        c.updateAAD(aadFor(recordId));
        return c.doFinal(row.ciphertext());      // AEADBadTagException on any tampering
    }

    /** ECDH + HKDF for encrypting to a recipient's public key (no shared secret sent). */
    public byte[] encryptTo(PublicKey recipient, byte[] plaintext) throws GeneralSecurityException {
        KeyPair ephemeral = keyPairGen("EC", 256);
        SecretKey shared = deriveSharedKey(ephemeral, recipient);
        byte[] salt = secureRandom(32);
        SecretKey kek = hkdf(shared, salt, "vaultkek:v1");
        byte[] iv = secureRandom(12);
        Cipher c = Cipher.getInstance("AES/GCM/NoPadding");
        c.init(ENCRYPT_MODE, kek, new GCMParameterSpec(128, iv));
        return concat(ephemeral.getPublic().getEncoded(), salt, iv, c.doFinal(plaintext));
    }
}
```

The demonstration that makes the mode choice obvious:

```java
@Test void ecbLeaksStructureAndGcmDoesNot() throws Exception {
    byte[][] records = { "AAAA".getBytes(), "BBBB".getBytes(), "CCCC".getBytes(), "AAAA".getBytes() };
    List<byte[]> ecb = records.stream().map(r -> encrypt("AES/ECB/PKCS5Padding", key, r)).toList();
    assertArrayEquals(ecb.get(0), ecb.get(3));   // identical plaintext -> identical block: leak

    List<byte[]> gcm = records.stream().map(r -> vault.seal(id++, r).ciphertext()).toList();
    assertFalse(Arrays.equals(gcm.get(0), gcm.get(3)));   // fresh nonce hides the pattern
}

@Test void tamperedCiphertextFailsAuthentication() {
    SealedRow row = vault.seal(42, "salary".getBytes());
    byte[] broken = row.ciphertext().clone();
    broken[0] ^= 0x01;
    assertThrows(AEADBadTagException.class, () -> vault.open(42, row.withCiphertext(broken)));
}

@Test void aadPreventsRowSwapping() {
    SealedRow a = vault.seal(1, "alice".getBytes());
    assertThrows(AEADBadTagException.class, () -> vault.open(2, a));  // ciphertext bound to id
}
```

### Deliverables

- [ ] AES-256-GCM seal/open with fresh 96-bit nonce per record and AAD binding
- [ ] KEK/DEK envelope encryption with a re-wrap-only rotation routine
- [ ] ECDH + HKDF-SHA256 path for encrypting to a recipient public key
- [ ] `rotateKek(oldId, newId)` that touches only the wrapped-key column
- [ ] ECB-vs-GCM leakage demonstration test
- [ ] Tamper tests: flipped ciphertext bit, swapped row, wrong keyId
- [ ] Key generation via `KeyPairGenerator`/`SecureRandom`; no hardcoded material
- [ ] README documenting the threat model each primitive defends against
