# Code Deep Dive: security-deep

## 1. AES-256-GCM Implementation

```java
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;
import javax.crypto.spec.SecretKeySpec;
import java.security.SecureRandom;
import java.util.Base64;

public class AESGCMDeepDive {
    private static final int GCM_IV_LENGTH = 12; // 96 bits recommended
    private static final int GCM_TAG_LENGTH = 16; // 128 bits
    private static final String ALGORITHM = "AES/GCM/NoPadding";

    public static byte[] encrypt(byte[] plaintext, SecretKey key) throws Exception {
        byte[] iv = new byte[GCM_IV_LENGTH];
        new SecureRandom().nextBytes(iv);
        
        Cipher cipher = Cipher.getInstance(ALGORITHM);
        GCMParameterSpec spec = new GCMParameterSpec(GCM_TAG_LENGTH * 8, iv);
        cipher.init(Cipher.ENCRYPT_MODE, key, spec);
        
        byte[] ciphertext = cipher.doFinal(plaintext);
        
        // Prepend IV for transmission
        byte[] result = new byte[GCM_IV_LENGTH + ciphertext.length];
        System.arraycopy(iv, 0, result, 0, GCM_IV_LENGTH);
        System.arraycopy(ciphertext, 0, result, GCM_IV_LENGTH, ciphertext.length);
        return result;
    }

    public static byte[] decrypt(byte[] encrypted, SecretKey key) throws Exception {
        byte[] iv = new byte[GCM_IV_LENGTH];
        System.arraycopy(encrypted, 0, iv, 0, GCM_IV_LENGTH);
        
        Cipher cipher = Cipher.getInstance(ALGORITHM);
        GCMParameterSpec spec = new GCMParameterSpec(GCM_TAG_LENGTH * 8, iv);
        cipher.init(Cipher.DECRYPT_MODE, key, spec);
        
        return cipher.doFinal(encrypted, GCM_IV_LENGTH, encrypted.length - GCM_IV_LENGTH);
    }
}
```

**Key insights:**
- GCM provides authenticated encryption (confidentiality + integrity)
- IV must be unique per encryption with the same key — never reuse
- The authentication tag is appended to ciphertext by the Cipher

## 2. JWT Validation Deep Dive

```java
import com.nimbusds.jose.JWSVerifier;
import com.nimbusds.jose.crypto.RSASSAVerifier;
import com.nimbusds.jwt.SignedJWT;
import java.security.interfaces.RSAPublicKey;
import java.util.Date;

public class JWTValidatorDeepDive {
    
    public static boolean validateToken(String token, RSAPublicKey publicKey, 
                                        String expectedIssuer, String expectedAudience) throws Exception {
        SignedJWT signedJWT = SignedJWT.parse(token);
        
        // 1. Verify signature
        JWSVerifier verifier = new RSASSAVerifier(publicKey);
        if (!signedJWT.verify(verifier)) {
            throw new SecurityException("Invalid JWT signature");
        }
        
        // 2. Verify claims
        var claims = signedJWT.getJWTClaimsSet();
        
        // Check expiration
        Date now = new Date();
        if (claims.getExpirationTime() != null && now.after(claims.getExpirationTime())) {
            throw new SecurityException("Token expired");
        }
        
        // Check not before
        if (claims.getNotBeforeTime() != null && now.before(claims.getNotBeforeTime())) {
            throw new SecurityException("Token not yet valid");
        }
        
        // Check issuer
        if (!expectedIssuer.equals(claims.getIssuer())) {
            throw new SecurityException("Invalid issuer");
        }
        
        // Check audience
        if (claims.getAudience() == null || !claims.getAudience().contains(expectedAudience)) {
            throw new SecurityException("Invalid audience");
        }
        
        return true;
    }
}
```

**Key insights:**
- Always verify signature before trusting any claims
- Check `exp`, `nbf`, `iss`, `aud` — all four are critical
- Use clock skew leeway (e.g., 30 seconds) for distributed systems

## 3. Rate Limiter Deep Dive

```java
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

public class TokenBucketRateLimiter {
    private final int capacity;
    private final int refillRate; // tokens per second
    private final ConcurrentHashMap<String, Bucket> buckets = new ConcurrentHashMap<>();
    
    private static class Bucket {
        AtomicInteger tokens;
        long lastRefillTimestamp;
        
        Bucket(int capacity) {
            this.tokens = new AtomicInteger(capacity);
            this.lastRefillTimestamp = System.currentTimeMillis();
        }
    }
    
    public TokenBucketRateLimiter(int capacity, int refillRate) {
        this.capacity = capacity;
        this.refillRate = refillRate;
    }
    
    public boolean allowRequest(String clientId) {
        Bucket bucket = buckets.computeIfAbsent(clientId, k -> new Bucket(capacity));
        refill(bucket);
        return bucket.tokens.getAndDecrement() > 0;
    }
    
    private void refill(Bucket bucket) {
        long now = System.currentTimeMillis();
        long elapsed = now - bucket.lastRefillTimestamp;
        int tokensToAdd = (int) (elapsed * refillRate / 1000);
        
        if (tokensToAdd > 0) {
            bucket.tokens.updateAndGet(current -> 
                Math.min(capacity, current + tokensToAdd));
            bucket.lastRefillTimestamp = now;
        }
    }
}
```

**Key insights:**
- Token bucket allows bursts up to capacity while maintaining average rate
- `ConcurrentHashMap` ensures thread safety for multi-threaded servers
- Refill is lazy — only computed when a request arrives

## 4. Password Hashing Deep Dive

```java
import org.bouncycastle.crypto.generators.Argon2BytesGenerator;
import org.bouncycastle.crypto.params.Argon2Parameters;
import java.security.SecureRandom;
import java.util.Base64;

public class Argon2DeepDive {
    private static final int SALT_LENGTH = 16;
    private static final int HASH_LENGTH = 32;
    private static final int ITERATIONS = 3;
    private static final int MEMORY = 65536; // 64 MB
    private static final int PARALLELISM = 1;
    
    public static String hashPassword(String password) {
        byte[] salt = new byte[SALT_LENGTH];
        new SecureRandom().nextBytes(salt);
        
        Argon2Parameters params = new Argon2Parameters.Builder(Argon2Parameters.ARGON2_id)
            .withSalt(salt)
            .withIterations(ITERATIONS)
            .withMemoryAsKB(MEMORY)
            .withParallelism(PARALLELISM)
            .build();
        
        Argon2BytesGenerator generator = new Argon2BytesGenerator();
        generator.init(params);
        
        byte[] hash = new byte[HASH_LENGTH];
        generator.generateBytes(password.toCharArray(), hash);
        
        // Format: $argon2id$v=19$m=65536,t=3,p=1$<salt>$<hash>
        return String.format("$argon2id$v=19$m=%d,t=%d,p=%d$%s$%s",
            MEMORY, ITERATIONS, PARALLELISM,
            Base64.getEncoder().encodeToString(salt),
            Base64.getEncoder().encodeToString(hash));
    }
}
```

**Key insights:**
- Argon2id is the winner of the Password Hashing Competition (2015)
- Memory-hard functions resist GPU/ASIC attacks
- Parameters should be tuned to your hardware — higher memory = more resistant to cracking

## 5. Zero Trust Policy Engine Deep Dive

```java
import java.util.List;
import java.util.Map;

public class ZeroTrustPolicyEngine {
    
    public enum Decision { ALLOW, DENY }
    
    public static class Policy {
        String name;
        Map<String, String> conditions; // e.g., "role" -> "admin", "devicePosture" -> "compliant"
        Decision decision;
    }
    
    public Decision evaluate(String identity, Map<String, String> context, List<Policy> policies) {
        // Default deny — if no policy matches, deny access
        for (Policy policy : policies) {
            if (matches(policy, context)) {
                logDecision(identity, policy, context);
                return policy.decision;
            }
        }
        logDecision(identity, null, context);
        return Decision.DENY; // Default deny
    }
    
    private boolean matches(Policy policy, Map<String, String> context) {
        for (Map.Entry<String, String> condition : policy.conditions.entrySet()) {
            String contextValue = context.get(condition.getKey());
            if (contextValue == null || !contextValue.equals(condition.getValue())) {
                return false;
            }
        }
        return true;
    }
    
    private void logDecision(String identity, Policy policy, Map<String, String> context) {
        // Audit log for all access decisions
        System.out.printf("[AUDIT] identity=%s policy=%s context=%s%n", 
            identity, policy != null ? policy.name : "DEFAULT_DENY", context);
    }
}
```

**Key insights:**
- Default-deny is the core principle — explicit allow only
- Every decision is logged for audit and forensics
- Policies should be evaluated on every request, not just at login
- Context includes identity, device posture, location, time, and behavior
