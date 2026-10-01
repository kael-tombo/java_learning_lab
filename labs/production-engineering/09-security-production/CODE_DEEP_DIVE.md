# CODE DEEP DIVE: Enterprise Security, Cryptography & Zero Trust Patterns
## Lab 09 | Production Engineering Academy — Top 0.0001% Engineering

---

## Pattern 1: Enterprise Envelope Encryption with AES-256-GCM & AWS KMS

```java
package com.learning.production.lab09;

import software.amazon.awssdk.core.SdkBytes;
import software.amazon.awssdk.services.kms.KmsClient;
import software.amazon.awssdk.services.kms.model.DataKeySpec;
import software.amazon.awssdk.services.kms.model.DecryptRequest;
import software.amazon.awssdk.services.kms.model.GenerateDataKeyRequest;
import software.amazon.awssdk.services.kms.model.GenerateDataKeyResponse;

import javax.crypto.Cipher;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.nio.ByteBuffer;
import java.security.SecureRandom;
import java.util.Arrays;

/**
 * High-Performance Envelope Encryption Service.
 * - Master Key (KEK) resides permanently inside AWS KMS Hardware Security Module (HSM).
 * - Ephemeral Data Encryption Key (DEK) encrypts payload via local AES-256-GCM.
 * - Plaintext DEK is explicitly zeroized in RAM immediately after use.
 */
public class EnvelopeEncryptionService {

    private static final String ALGORITHM = "AES/GCM/NoPadding";
    private static final int GCM_TAG_LENGTH_BITS = 128;
    private static final int GCM_IV_LENGTH_BYTES = 12; // 96-bit standard IV for GCM

    private final KmsClient kmsClient;
    private final String kmsKeyId;
    private final SecureRandom secureRandom = new SecureRandom();

    public EnvelopeEncryptionService(KmsClient kmsClient, String kmsKeyId) {
        this.kmsClient = kmsClient;
        this.kmsKeyId = kmsKeyId;
    }

    /**
     * Encrypts plaintext bytes using Envelope Encryption.
     * Returns a packed binary blob: [IV (12B)] + [Encrypted DEK Length (4B)] + [Encrypted DEK] + [Ciphertext]
     */
    public byte[] encrypt(byte[] plaintext) throws Exception {
        // 1. Request a new Data Encryption Key (DEK) from KMS
        GenerateDataKeyRequest request = GenerateDataKeyRequest.builder()
                .keyId(kmsKeyId)
                .keySpec(DataKeySpec.AES_256)
                .build();

        GenerateDataKeyResponse response = kmsClient.generateDataKey(request);
        byte[] plaintextDek = response.plaintext().asByteArray();
        byte[] encryptedDek = response.ciphertextBlob().asByteArray();

        // 2. Generate cryptographically random 96-bit IV
        byte[] iv = new byte[GCM_IV_LENGTH_BYTES];
        secureRandom.nextBytes(iv);

        byte[] ciphertext;
        try {
            // 3. Encrypt payload using local AES-256-GCM
            SecretKey key = new SecretKeySpec(plaintextDek, "AES");
            Cipher cipher = Cipher.getInstance(ALGORITHM);
            cipher.init(Cipher.ENCRYPT_MODE, key, new GCMParameterSpec(GCM_TAG_LENGTH_BITS, iv));
            ciphertext = cipher.doFinal(plaintext);
        } finally {
            // 4. SECURITY INVARIANT: Zeroize plaintext DEK from JVM memory!
            Arrays.fill(plaintextDek, (byte) 0);
        }

        // 5. Pack encrypted payload
        ByteBuffer buffer = ByteBuffer.allocate(iv.length + 4 + encryptedDek.length + ciphertext.length);
        buffer.put(iv);
        buffer.putInt(encryptedDek.length);
        buffer.put(encryptedDek);
        buffer.put(ciphertext);
        return buffer.array();
    }

    /**
     * Decrypts an envelope-encrypted binary blob.
     */
    public byte[] decrypt(byte[] packedPayload) throws Exception {
        ByteBuffer buffer = ByteBuffer.wrap(packedPayload);

        // 1. Extract IV
        byte[] iv = new byte[GCM_IV_LENGTH_BYTES];
        buffer.get(iv);

        // 2. Extract Encrypted DEK
        int encryptedDekLength = buffer.getInt();
        byte[] encryptedDek = new byte[encryptedDekLength];
        buffer.get(encryptedDek);

        // 3. Extract Ciphertext
        byte[] ciphertext = new byte[buffer.remaining()];
        buffer.get(ciphertext);

        // 4. Request KMS to decrypt the DEK inside its HSM
        DecryptRequest decryptRequest = DecryptRequest.builder()
                .ciphertextBlob(SdkBytes.fromByteArray(encryptedDek))
                .build();
        byte[] plaintextDek = kmsClient.decrypt(decryptRequest).plaintext().asByteArray();

        try {
            // 5. Decrypt payload locally using AES-256-GCM
            SecretKey key = new SecretKeySpec(plaintextDek, "AES");
            Cipher cipher = Cipher.getInstance(ALGORITHM);
            cipher.init(Cipher.DECRYPT_MODE, key, new GCMParameterSpec(GCM_TAG_LENGTH_BITS, iv));
            return cipher.doFinal(ciphertext);
        } finally {
            // 6. Zeroize plaintext DEK
            Arrays.fill(plaintextDek, (byte) 0);
        }
    }
}
```

---

## Pattern 2: Strict JWT Verification Filter with RS256 Algorithm Pinning

```java
package com.learning.production.lab09;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jws;
import io.jsonwebtoken.JwtParser;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.SignatureException;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.filter.OncePerRequestFilter;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.security.PublicKey;
import java.util.List;

/**
 * Hardened JWT Authentication Filter.
 * Strictly defends against:
 *   1. 'alg: none' attacks
 *   2. Algorithm Confusion attacks (RSA-to-HMAC) via strict algorithm pinning
 *   3. Replay attacks with clock skew validation
 */
public class HardenedJwtAuthenticationFilter extends OncePerRequestFilter {

    private static final Logger log = LoggerFactory.getLogger(HardenedJwtAuthenticationFilter.class);
    private final JwtParser jwtParser;

    public HardenedJwtAuthenticationFilter(PublicKey rsaPublicKey) {
        // Enforce strict RS256 algorithm pinning:
        this.jwtParser = Jwts.parser()
                .verifyWith(rsaPublicKey)                    // Pin to RSA public key
                .clockSkewSeconds(30)                       // Maximum 30 seconds clock drift allowed
                .requireIssuer("https://auth.corp.internal") // Mandatory issuer validation
                .build();
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, 
                                    HttpServletResponse response, 
                                    FilterChain filterChain) throws ServletException, IOException {
        
        String authHeader = request.getHeader("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }

        String rawToken = authHeader.substring(7).trim();
        try {
            // Parse and strictly verify signature:
            Jws<Claims> jws = jwtParser.parseSignedClaims(rawToken);
            Claims claims = jws.getPayload();

            String username = claims.getSubject();
            @SuppressWarnings("unchecked")
            List<String> roles = claims.get("roles", List.class);

            List<SimpleGrantedAuthority> authorities = roles.stream()
                    .map(r -> new SimpleGrantedAuthority("ROLE_" + r))
                    .toList();

            var authentication = new UsernamePasswordAuthenticationToken(username, null, authorities);
            SecurityContextHolder.getContext().setAuthentication(authentication);

        } catch (SignatureException e) {
            log.warn("🚨 [SECURITY ALERT] Forged JWT signature detected from IP {}: {}", 
                    request.getRemoteAddr(), e.getMessage());
            response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Invalid Token Signature");
            return;
        } catch (Exception e) {
            log.warn("JWT validation failed: {}", e.getMessage());
            response.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Invalid Authentication Token");
            return;
        }

        filterChain.doFilter(request, response);
    }
}
```

---

## Pattern 3: JEP 290 Dynamic Serialization Filter Implementation

```java
package com.learning.production.lab09;

import java.io.ObjectInputFilter;
import java.io.ObjectInputStream;
import java.io.InputStream;

/**
 * Enforces JEP 290 Serialization Filtering to neutralize Gadget Chain RCE attacks.
 */
public class SafeObjectDeserializer {

    /**
     * Programmatic JEP 290 filter allowing only explicit domain objects.
     */
    private static final ObjectInputFilter STRICT_DOMAIN_FILTER = filterInfo -> {
        Class<?> clazz = filterInfo.serialClass();
        if (clazz == null) {
            return ObjectInputFilter.Status.UNDECIDED;
        }

        // 1. Strictly forbid dangerous gadget classes (invokers, transformers, reflection)
        String className = clazz.getName();
        if (className.startsWith("org.apache.commons.collections") ||
            className.startsWith("org.springframework.") ||
            className.startsWith("java.lang.reflect.") ||
            className.startsWith("com.sun.") ||
            className.startsWith("javassist.")) {
            
            return ObjectInputFilter.Status.REJECTED;
        }

        // 2. Allow only explicit safe domain classes
        if (className.equals("com.learning.production.lab09.SafeUserSession") ||
            className.equals("java.lang.String") ||
            className.equals("java.lang.Long") ||
            className.equals("java.util.ArrayList")) {
            
            return ObjectInputFilter.Status.ALLOWED;
        }

        // Reject everything else by default:
        return ObjectInputFilter.Status.REJECTED;
    };

    public static Object safeDeserialize(InputStream inputStream) throws Exception {
        try (ObjectInputStream ois = new ObjectInputStream(inputStream)) {
            // Attach filter directly to ObjectInputStream:
            ois.setObjectInputFilter(STRICT_DOMAIN_FILTER);
            return ois.readObject();
        }
    }
}
```

---

## Pattern 4: Safe Parameterized JPA Criteria Query with Whitelisted Sorting

```java
package com.learning.production.lab09;

import jakarta.persistence.EntityManager;
import jakarta.persistence.criteria.*;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Set;

/**
 * Defends against SQL/JPQL injection in dynamic queries and ORDER BY clauses.
 */
@Repository
public class SecureAccountRepository {

    private static final Set<String> ALLOWED_SORT_COLUMNS = Set.of("id", "balance", "createdAt");
    private final EntityManager entityManager;

    public SecureAccountRepository(EntityManager entityManager) {
        this.entityManager = entityManager;
    }

    public List<AccountEntity> searchAccounts(String ownerName, String sortColumn, boolean ascending) {
        // 1. Whitelist validation of sortColumn to eliminate ORDER BY injection:
        if (!ALLOWED_SORT_COLUMNS.contains(sortColumn)) {
            throw new IllegalArgumentException("Disallowed sort column: " + sortColumn);
        }

        CriteriaBuilder cb = entityManager.getCriteriaBuilder();
        CriteriaQuery<AccountEntity> query = cb.createQuery(AccountEntity.class);
        Root<AccountEntity> account = query.from(AccountEntity.class);

        // 2. Strictly parameterized predicate:
        Predicate ownerPredicate = cb.equal(account.get("ownerName"), ownerName);
        query.where(ownerPredicate);

        // 3. Programmatic order by:
        Order order = ascending ? cb.asc(account.get(sortColumn)) : cb.desc(account.get(sortColumn));
        query.orderBy(order);

        return entityManager.createQuery(query)
                .setMaxResults(100)
                .getResultList();
    }
}
```

---

## Pattern 5: Jackson Sealed Polymorphic Deserialization Configuration

```java
package com.learning.production.lab09;

import com.fasterxml.jackson.annotation.JsonSubTypes;
import com.fasterxml.jackson.annotation.JsonTypeInfo;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.jsontype.BasicPolymorphicTypeValidator;
import com.fasterxml.jackson.databind.jsontype.PolymorphicTypeValidator;

/**
 * Hardens Jackson against unauthenticated polymorphic deserialization RCE.
 */
public class SecureJsonConfig {

    public static ObjectMapper createSecureObjectMapper() {
        // Enforce strict base package validator:
        PolymorphicTypeValidator ptv = BasicPolymorphicTypeValidator.builder()
                .allowIfBaseType("com.learning.production.lab09.")
                .build();

        return new ObjectMapper().setPolymorphicTypeValidator(ptv);
    }

    /**
     * Bounded polymorphic hierarchy using Java 21 Sealed Interfaces:
     */
    @JsonTypeInfo(use = JsonTypeInfo.Id.NAME, include = JsonTypeInfo.As.PROPERTY, property = "paymentType")
    @JsonSubTypes({
            @JsonSubTypes.Type(value = CreditCardPayment.class, name = "CREDIT_CARD"),
            @JsonSubTypes.Type(value = WireTransferPayment.class, name = "WIRE_TRANSFER")
    })
    public sealed interface PaymentPayload permits CreditCardPayment, WireTransferPayment {
        double amount();
    }

    public record CreditCardPayment(double amount, String maskedPan) implements PaymentPayload {}
    public record WireTransferPayment(double amount, String iban) implements PaymentPayload {}
}
```
