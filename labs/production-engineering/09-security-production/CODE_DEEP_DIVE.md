# CODE DEEP DIVE: Production Security Engineering Patterns
## Lab 09 | Production Engineering Academy

---

## Pattern 1: AES-256-GCM Envelope Encryption with Cryptographic Nonce

```java
package com.learning.production.lab09;

import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.nio.ByteBuffer;
import java.nio.charset.StandardCharsets;
import java.security.SecureRandom;
import java.util.Base64;

public class ProductionEnvelopeEncryptor {
    private static final String ALGORITHM = "AES/GCM/NoPadding";
    private static final int GCM_TAG_LENGTH_BITS = 128;
    private static final int GCM_IV_LENGTH_BYTES = 12; // 96-bit IV recommended by NIST
    private static final SecureRandom SECURE_RANDOM = new SecureRandom();

    /**
     * Encrypts plaintext using AES-256-GCM.
     * Output format: [12-byte IV] + [Ciphertext + 16-byte Auth Tag]
     */
    public static String encrypt(String plaintext, byte[] dataEncryptionKey) throws Exception {
        byte[] iv = new byte[GCM_IV_LENGTH_BYTES];
        SECURE_RANDOM.nextBytes(iv); // Cryptographically strong random IV

        Cipher cipher = Cipher.getInstance(ALGORITHM);
        SecretKey key = new SecretKeySpec(dataEncryptionKey, "AES");
        GCMParameterSpec parameterSpec = new GCMParameterSpec(GCM_TAG_LENGTH_BITS, iv);
        cipher.init(Cipher.ENCRYPT_MODE, key, parameterSpec);

        byte[] ciphertext = cipher.doFinal(plaintext.getBytes(StandardCharsets.UTF_8));

        // Pack IV and Ciphertext together
        ByteBuffer byteBuffer = ByteBuffer.allocate(iv.length + ciphertext.length);
        byteBuffer.put(iv);
        byteBuffer.put(ciphertext);

        return Base64.getEncoder().encodeToString(byteBuffer.array());
    }

    /**
     * Decrypts ciphertext and verifies GCM authentication tag.
     */
    public static String decrypt(String base64Payload, byte[] dataEncryptionKey) throws Exception {
        byte[] decoded = Base64.getDecoder().decode(base64Payload);
        ByteBuffer byteBuffer = ByteBuffer.wrap(decoded);

        byte[] iv = new byte[GCM_IV_LENGTH_BYTES];
        byteBuffer.get(iv);

        byte[] ciphertext = new byte[byteBuffer.remaining()];
        byteBuffer.get(ciphertext);

        Cipher cipher = Cipher.getInstance(ALGORITHM);
        SecretKey key = new SecretKeySpec(dataEncryptionKey, "AES");
        GCMParameterSpec parameterSpec = new GCMParameterSpec(GCM_TAG_LENGTH_BITS, iv);
        cipher.init(Cipher.DECRYPT_MODE, key, parameterSpec);

        byte[] plaintext = cipher.doFinal(ciphertext);
        return new String(plaintext, StandardCharsets.UTF_8);
    }
}
```

---

## Pattern 2: SSRF-Safe HTTP Client Validator

```java
package com.learning.production.lab09;

import java.net.InetAddress;
import java.net.URI;
import java.net.UnknownHostException;

public class SsrfSafetyValidator {

    /**
     * Validates that a user-supplied URI does NOT resolve to private, loopback, or metadata addresses.
     */
    public static void validateTargetUri(String uriString) throws UnknownHostException, SecurityException {
        URI uri = URI.create(uriString);
        String host = uri.getHost();

        if (host == null) {
            throw new SecurityException("Invalid URI host");
        }

        // Prohibit non-HTTP protocols (e.g. file://, gopher://, ldap://)
        String scheme = uri.getScheme();
        if (!"http".equalsIgnoreCase(scheme) && !"https".equalsIgnoreCase(scheme)) {
            throw new SecurityException("Unsupported protocol: " + scheme);
        }

        // Resolve DNS and inspect all resolved IP addresses
        InetAddress[] addresses = InetAddress.getAllByName(host);
        for (InetAddress addr : addresses) {
            if (addr.isLoopbackAddress() || addr.isSiteLocalAddress() || addr.isLinkLocalAddress() || addr.isAnyLocalAddress()) {
                throw new SecurityException("Blocked SSRF attempt to internal network address: " + addr.getHostAddress());
            }

            // Explicitly block AWS/GCP/Azure Metadata Services (169.254.169.254)
            String ip = addr.getHostAddress();
            if (ip.startsWith("169.254.") || ip.startsWith("10.") || ip.startsWith("192.168.") || ip.startsWith("127.")) {
                throw new SecurityException("Blocked SSRF attempt to metadata/private IP: " + ip);
            }
        }
    }
}
```
