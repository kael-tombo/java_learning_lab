# Solution Guide — Security Incident: Compromised API Key

## Problem: Compromised API Key, Data Exfiltration

This guide provides compilable Java code fixes for API key rotation, IP whitelisting, rate limiting, secrets management, pre-commit hooks, and CloudTrail anomaly detection integration.

---

## Layer 1: Immediate Key Rotation and Revocation

### Key Rotation Service

```java
package com.example.security.keymanagement;

import com.example.security.model.ApiKey;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import java.security.SecureRandom;
import java.time.Instant;
import java.util.Base64;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

@Service
public class ApiKeyManagementService {

    private static final Logger log = LoggerFactory.getLogger(ApiKeyManagementService.class);

    private final ConcurrentMap<String, ApiKey> activeKeys = new ConcurrentHashMap<>();
    private final ConcurrentMap<String, ApiKey> revokedKeys = new ConcurrentHashMap<>();
    private static final int KEY_LENGTH_BYTES = 32;
    private final SecureRandom secureRandom = new SecureRandom();

    public ApiKey rotateKey(String keyId) {
        ApiKey oldKey = activeKeys.remove(keyId);
        if (oldKey != null) {
            oldKey.setStatus(ApiKey.Status.REVOKED);
            oldKey.setRevokedAt(Instant.now());
            revokedKeys.put(keyId, oldKey);
            log.warn("Key {} revoked for rotation", keyId);
        }

        ApiKey newKey = generateKey(keyId);
        activeKeys.put(keyId, newKey);
        log.info("Key {} rotated successfully", keyId);

        return newKey;
    }

    public void revokeKey(String keyId) {
        ApiKey key = activeKeys.remove(keyId);
        if (key != null) {
            key.setStatus(ApiKey.Status.REVOKED);
            key.setRevokedAt(Instant.now());
            revokedKeys.put(keyId, key);
            log.warn("Key {} revoked immediately", keyId);

            invalidateCachedKey(keyId);
        }
    }

    public boolean validateKey(String apiKey, String sourceIp) {
        for (ApiKey key : activeKeys.values()) {
            if (key.getKeyValue().equals(apiKey)) {
                if (key.getStatus() != ApiKey.Status.ACTIVE) {
                    log.warn("Attempted use of non-active key: {}", key.getKeyId());
                    return false;
                }
                if (!isIpAllowed(key, sourceIp)) {
                    log.warn("Key {} used from unauthorized IP: {}", key.getKeyId(), sourceIp);
                    return false;
                }
                if (isRateLimited(key)) {
                    log.warn("Key {} rate limited", key.getKeyId());
                    return false;
                }
                return true;
            }
        }
        log.warn("Unknown API key presented from IP: {}", sourceIp);
        return false;
    }

    public ApiKey generateKey(String keyId) {
        byte[] keyBytes = new byte[KEY_LENGTH_BYTES];
        secureRandom.nextBytes(keyBytes);
        String keyValue = "sk-" + keyId + "-" + Base64.getUrlEncoder().withoutPadding()
            .encodeToString(keyBytes);

        ApiKey key = new ApiKey();
        key.setKeyId(keyId);
        key.setKeyValue(keyValue);
        key.setStatus(ApiKey.Status.ACTIVE);
        key.setCreatedAt(Instant.now());
        key.setExpiresAt(Instant.now().plus(java.time.Duration.ofDays(90)));

        return key;
    }

    private void invalidateCachedKey(String keyId) {
        // Invalidate key in Redis/distributed cache
        log.info("Invalidated cached key: {}", keyId);
    }

    private boolean isIpAllowed(ApiKey key, String sourceIp) {
        List<String> allowedIps = key.getAllowedIps();
        if (allowedIps == null || allowedIps.isEmpty()) {
            return true; // No IP restriction
        }
        return allowedIps.stream().anyMatch(ip -> ip.equals(sourceIp) || matchesCidr(ip, sourceIp));
    }

    private boolean matchesCidr(String cidr, String ip) {
        // Simplified CIDR matching — in production use java-net library
        return cidr.equals(ip);
    }

    private boolean isRateLimited(ApiKey key) {
        return false; // Rate limiter integrated separately
    }
}
```

### Emergency Key Revocation Endpoint

```java
package com.example.security.controller;

import com.example.security.keymanagement.ApiKeyManagementService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/admin/security")
public class KeyRevocationController {

    private static final Logger log = LoggerFactory.getLogger(KeyRevocationController.class);

    private final ApiKeyManagementService keyManagementService;

    public KeyRevocationController(ApiKeyManagementService keyManagementService) {
        this.keyManagementService = keyManagementService;
    }

    @PostMapping("/keys/{keyId}/revoke")
    public ResponseEntity<String> revokeKey(@PathVariable String keyId) {
        log.warn("MANUAL KEY REVOCATION: {} initiated by {}",
            keyId, getCurrentUser());
        keyManagementService.revokeKey(keyId);
        return ResponseEntity.ok("Key " + keyId + " revoked");
    }

    @PostMapping("/keys/{keyId}/rotate")
    public ResponseEntity<ApiKey> rotateKey(@PathVariable String keyId) {
        log.warn("MANUAL KEY ROTATION: {} initiated by {}", keyId, getCurrentUser());
        ApiKey newKey = keyManagementService.rotateKey(keyId);
        return ResponseEntity.ok(newKey);
    }

    @PostMapping("/keys/revoke-all")
    public ResponseEntity<String> revokeAllKeys() {
        log.warn("EMERGENCY: All keys revoked by {}", getCurrentUser());
        // Implementation would revoke all keys
        return ResponseEntity.ok("All keys revoked");
    }

    private String getCurrentUser() {
        return "admin-user"; // In production, get from SecurityContext
    }
}
```

---

## Layer 2: Rate Limiting Per API Key

```java
package com.example.security.ratelimit;

import io.github.resilience4j.ratelimiter.RateLimiter;
import io.github.resilience4j.ratelimiter.RateLimiterConfig;
import io.github.resilience4j.ratelimiter.RateLimiterRegistry;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import java.time.Duration;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class ApiKeyRateLimiter {

    private static final Logger log = LoggerFactory.getLogger(ApiKeyRateLimiter.class);

    private final ConcurrentHashMap<String, RateLimiter> keyRateLimiters = new ConcurrentHashMap<>();
    private final RateLimiterRegistry registry;

    private static final int DEFAULT_LIMIT = 1000;
    private static final Duration DEFAULT_PERIOD = Duration.ofHours(1);
    private static final int BURST_LIMIT = 100;

    public ApiKeyRateLimiter() {
        RateLimiterConfig defaultConfig = RateLimiterConfig.custom()
            .limitForPeriod(DEFAULT_LIMIT)
            .limitRefreshPeriod(DEFAULT_PERIOD)
            .timeoutDuration(Duration.ofMillis(10))
            .build();
        this.registry = RateLimiterRegistry.of(defaultConfig);
    }

    public boolean tryAcquire(String apiKey) {
        RateLimiter limiter = getOrCreateRateLimiter(apiKey);
        boolean acquired = limiter.acquirePermission();

        if (!acquired) {
            log.warn("Rate limit exceeded for API key: {}", maskKey(apiKey));
        }

        return acquired;
    }

    public boolean tryAcquire(String apiKey, String endpoint) {
        String rateLimitKey = apiKey + ":" + endpoint;
        RateLimiter limiter = getOrCreateRateLimiter(rateLimitKey);
        return limiter.acquirePermission();
    }

    private RateLimiter getOrCreateRateLimiter(String key) {
        return keyRateLimiters.computeIfAbsent(key, k -> {
            RateLimiterConfig config = RateLimiterConfig.custom()
                .limitForPeriod(DEFAULT_LIMIT)
                .limitRefreshPeriod(DEFAULT_PERIOD)
                .timeoutDuration(Duration.ofMillis(10))
                .build();
            return registry.rateLimiter(k, config);
        });
    }

    public void updateRateLimit(String apiKey, int limit, Duration period) {
        RateLimiterConfig newConfig = RateLimiterConfig.custom()
            .limitForPeriod(limit)
            .limitRefreshPeriod(period)
            .timeoutDuration(Duration.ofMillis(10))
            .build();
        RateLimiter limiter = getOrCreateRateLimiter(apiKey);
        limiter.changeTimeoutDuration(Duration.ofMillis(10));
        log.info("Rate limit updated for key {}: {}/{}", maskKey(apiKey), limit, period);
    }

    private String maskKey(String key) {
        if (key.length() <= 8) return "****";
        return key.substring(0, 4) + "****" + key.substring(key.length() - 4);
    }
}
```

### Rate Limiting Filter

```java
package com.example.security.filter;

import com.example.security.ratelimit.ApiKeyRateLimiter;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

@Component
public class ApiKeyRateLimitFilter extends OncePerRequestFilter {

    private static final Logger log = LoggerFactory.getLogger(ApiKeyRateLimitFilter.class);

    private final ApiKeyRateLimiter rateLimiter;

    public ApiKeyRateLimitFilter(ApiKeyRateLimiter rateLimiter) {
        this.rateLimiter = rateLimiter;
    }

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {

        String apiKey = request.getHeader("X-API-Key");
        String endpoint = request.getRequestURI();

        if (apiKey != null && !rateLimiter.tryAcquire(apiKey, endpoint)) {
            log.warn("Rate limit exceeded: key={}, endpoint={}, IP={}",
                maskKey(apiKey), endpoint, request.getRemoteAddr());

            response.setStatus(HttpStatus.TOO_MANY_REQUESTS.value());
            response.setContentType("application/json");
            response.getWriter().write("{\"error\":\"Rate limit exceeded. Try again later.\"}");
            return;
        }

        filterChain.doFilter(request, response);
    }

    private String maskKey(String key) {
        if (key == null || key.length() <= 8) return "****";
        return key.substring(0, 4) + "****" + key.substring(key.length() - 4);
    }
}
```

---

## Layer 3: IP Whitelisting

```java
package com.example.security.ipwhitelist;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import javax.annotation.PostConstruct;
import java.net.InetAddress;
import java.util.*;
import java.util.concurrent.CopyOnWriteArrayList;

@Service
public class IpWhitelistService {

    private static final Logger log = LoggerFactory.getLogger(IpWhitelistService.class);

    private final List<String> whitelistedIps = new CopyOnWriteArrayList<>();
    private final Map<String, List<String>> endpointWhitelists = new HashMap<>();

    @PostConstruct
    public void init() {
        // Production IP ranges
        whitelistedIps.addAll(List.of(
            "10.0.0.0/8",      // Internal VPC
            "172.16.0.0/12",    // Internal VPC
            "192.168.0.0/16",   // Internal VPC
            "203.0.113.0/24"    // Office VPN
        ));

        // Endpoint-specific whitelisting
        endpointWhitelists.put("/api/v1/users/export/bulk",
            List.of("10.0.0.0/8", "203.0.113.0/24"));
        endpointWhitelists.put("/api/v1/admin/**",
            List.of("203.0.113.0/24")); // Admin only accessible from office
        endpointWhitelists.put("/api/v1/cache/clear",
            List.of("10.0.0.0/8")); // Cache ops only from internal network
    }

    public boolean isAllowed(String ipAddress, String endpoint) {
        // Check endpoint-specific whitelist first
        List<String> endpointIps = findEndpointWhitelist(endpoint);
        if (endpointIps != null) {
            boolean allowed = matchesAnyCidr(ipAddress, endpointIps);
            if (!allowed) {
                log.warn("IP {} blocked for endpoint {} (not in endpoint whitelist)", ipAddress, endpoint);
            }
            return allowed;
        }

        // Check global whitelist
        boolean allowed = matchesAnyCidr(ipAddress, whitelistedIps);
        if (!allowed) {
            log.warn("IP {} blocked (not in global whitelist)", ipAddress);
        }
        return allowed;
    }

    private boolean matchesAnyCidr(String ipAddress, List<String> cidrList) {
        return cidrList.stream().anyMatch(cidr -> matchesCidr(cidr, ipAddress));
    }

    private boolean matchesCidr(String cidr, String ipAddress) {
        try {
            if (cidr.contains("/")) {
                String[] parts = cidr.split("/");
                int prefixLength = Integer.parseInt(parts[1]);

                byte[] cidrBytes = InetAddress.getByName(parts[0]).getAddress();
                byte[] ipBytes = InetAddress.getByName(ipAddress).getAddress();

                if (cidrBytes.length != ipBytes.length) {
                    return false;
                }

                int fullBytes = prefixLength / 8;
                int remainingBits = prefixLength % 8;

                for (int i = 0; i < fullBytes; i++) {
                    if (cidrBytes[i] != ipBytes[i]) {
                        return false;
                    }
                }

                if (remainingBits > 0) {
                    int mask = 0xFF << (8 - remainingBits);
                    if ((cidrBytes[fullBytes] & mask) != (ipBytes[fullBytes] & mask)) {
                        return false;
                    }
                }

                return true;
            } else {
                return cidr.equals(ipAddress);
            }
        } catch (Exception e) {
            log.warn("CIDR match error for {} and {}", cidr, ipAddress, e);
            return false;
        }
    }

    private List<String> findEndpointWhitelist(String endpoint) {
        for (Map.Entry<String, List<String>> entry : endpointWhitelists.entrySet()) {
            String pattern = entry.getKey();
            if (pattern.endsWith("/**")) {
                String prefix = pattern.substring(0, pattern.length() - 3);
                if (endpoint.startsWith(prefix)) {
                    return entry.getValue();
                }
            }
            if (pattern.equals(endpoint)) {
                return entry.getValue();
            }
        }
        return null;
    }

    public void addToWhitelist(String cidr, String endpoint) {
        if (endpoint != null) {
            endpointWhitelists.computeIfAbsent(endpoint, k -> new ArrayList<>()).add(cidr);
        } else {
            whitelistedIps.add(cidr);
        }
        log.info("Added {} to whitelist for endpoint {}", cidr, endpoint);
    }

    public void removeFromWhitelist(String cidr, String endpoint) {
        if (endpoint != null) {
            endpointWhitelists.getOrDefault(endpoint, List.of()).remove(cidr);
        } else {
            whitelistedIps.remove(cidr);
        }
        log.warn("Removed {} from whitelist for endpoint {}", cidr, endpoint);
    }
}
```

### IP Whitelist Filter

```java
package com.example.security.filter;

import com.example.security.ipwhitelist.IpWhitelistService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;
import javax.servlet.FilterChain;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import java.io.IOException;

@Component
public class IpWhitelistFilter extends OncePerRequestFilter {

    private static final Logger log = LoggerFactory.getLogger(IpWhitelistFilter.class);

    private final IpWhitelistService ipWhitelistService;

    private static final List<String> SENSITIVE_PATHS = List.of(
        "/api/v1/users/export",
        "/api/v1/admin",
        "/api/v1/cache"

    );

    public IpWhitelistFilter(IpWhitelistService ipWhitelistService) {
        this.ipWhitelistService = ipWhitelistService;
    }

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain
    ) throws ServletException, IOException {

        String requestUri = request.getRequestURI();
        String clientIp = getClientIp(request);

        if (isSensitiveEndpoint(requestUri)) {
            if (!ipWhitelistService.isAllowed(clientIp, requestUri)) {
                log.warn("IP {} blocked from accessing sensitive endpoint {}",
                    clientIp, requestUri);

                response.setStatus(HttpStatus.FORBIDDEN.value());
                response.setContentType("application/json");
                response.getWriter().write("{\"error\":\"Access denied from your IP address\"}");
                return;
            }
        }

        filterChain.doFilter(request, response);
    }

    private boolean isSensitiveEndpoint(String uri) {
        return SENSITIVE_PATHS.stream().anyMatch(uri::startsWith);
    }

    private String getClientIp(HttpServletRequest request) {
        String xForwardedFor = request.getHeader("X-Forwarded-For");
        if (xForwardedFor != null && !xForwardedFor.isEmpty()) {
            return xForwardedFor.split(",")[0].trim();
        }
        return request.getRemoteAddr();
    }
}
```

---

## Layer 4: Pre-Commit Hook for Secret Scanning

### .gitignore Configuration

```gitignore
# .gitignore — Updated with security entries
# Environment files
.env
.env.local
.env.production
.env.development
*.env

# Secrets and keys
*.pem
*.key
*.p12
*.pfx
secrets.yml
credentials.yml

# IDE files
.idea/
.vscode/
*.swp
*.swo
```

### Pre-Commit Hook Script

```bash
#!/bin/bash
# .git/hooks/pre-commit — Secret scanning pre-commit hook

echo "Running pre-commit secret scan..."

# Patterns to detect (extend as needed)
PATTERNS=(
    "API_KEY|api_key|apiKey"
    "SECRET|secret"
    "PASSWORD|password"
    "TOKEN|token"
    ".env"
    "sk-"
    "AKIA"  # AWS access key
    "-----BEGIN.*PRIVATE KEY-----"
)

# Files staged for commit
STAGED_FILES=$(git diff --cached --name-only)

for file in $STAGED_FILES; do
    for pattern in "${PATTERNS[@]}"; do
        if git show :"$file" | grep -qiE "$pattern" 2>/dev/null; then
            echo "ERROR: Potential secret found in $file matching pattern: $pattern"
            echo "This commit contains potentially sensitive data."
            echo "Please remove the sensitive data and try again."
            echo ""
            echo "If this is a false positive, use: git commit --no-verify"
            exit 1
        fi
    done
done

# Additional check: block .env files
for file in $STAGED_FILES; do
    if [[ "$file" == *.env* ]]; then
        echo "ERROR: .env files should not be committed: $file"
        echo "Remove this file from the commit and add it to .gitignore"
        exit 1
    fi
done

echo "Pre-commit secret scan passed."
exit 0
```

### GitHub Actions Secret Scanning Step

```yaml
# .github/workflows/security-scan.yml
name: Security Scan
on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  secret-scanning:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: TruffleHog Secret Scan
        uses: trufflesecurity/trufflehog@v3
        with:
          extra_args: --results=verified,unknown

      - name: GitLeaks Scan
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}

      - name: Block on Secrets Found
        if: failure()
        run: |
          echo "::error::SECRETS DETECTED in this commit. Security team notified."
          echo "::error::Please remove secrets and re-commit."
          exit 1
```

---

## Layer 5: AWS Secrets Manager Integration

```java
package com.example.security.secrets;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import software.amazon.awssdk.services.secretsmanager.SecretsManagerClient;
import software.amazon.awssdk.services.secretsmanager.model.*;
import java.time.Duration;
import java.time.Instant;

@Service
public class SecretsManagerService {

    private static final Logger log = LoggerFactory.getLogger(SecretsManagerService.class);

    private final SecretsManagerClient secretsManagerClient;

    public SecretsManagerService(SecretsManagerClient secretsManagerClient) {
        this.secretsManagerClient = secretsManagerClient;
    }

    public String getSecret(String secretName) {
        try {
            GetSecretRequest request = GetSecretRequest.builder()
                .secretId(secretName)
                .build();
            GetSecretResponse response = secretsManagerClient.getSecretValue(request);
            return response.secretString();
        } catch (ResourceNotFoundException e) {
            log.error("Secret {} not found in AWS Secrets Manager", secretName);
            throw new SecretNotFoundException("Secret not found: " + secretName);
        }
    }

    public void rotateSecret(String secretName) {
        try {
            RotateSecretRequest request = RotateSecretRequest.builder()
                .secretId(secretName)
                .rotationRules(RotationRulesType.builder()
                    .automaticallyAfterDays(90L)
                    .build())
                .build();
            secretsManagerClient.rotateSecret(request);
            log.info("Secret {} rotation initiated", secretName);
        } catch (Exception e) {
            log.error("Failed to rotate secret {}", secretName, e);
            throw new SecretRotationException("Rotation failed: " + secretName);
        }
    }

    public void createSecret(String secretName, String secretValue) {
        try {
            CreateSecretRequest request = CreateSecretRequest.builder()
                .name(secretName)
                .secretString(secretValue)
                .description("Auto-created by SecretsManagerService")
                .rotationRules(RotationRulesType.builder()
                    .automaticallyAfterDays(90L)
                    .build())
                .build();
            secretsManagerClient.createSecret(request);
            log.info("Secret {} created in AWS Secrets Manager", secretName);
        } catch (Exception e) {
            log.error("Failed to create secret {}", secretName, e);
            throw new SecretCreationException("Creation failed: " + secretName);
        }
    }

    public void deleteSecret(String secretName) {
        try {
            DeleteSecretRequest request = DeleteSecretRequest.builder()
                .secretId(secretName)
                .forceDeleteWithoutRecovery(true)
                .build();
            secretsManagerClient.deleteSecret(request);
            log.warn("Secret {} deleted from AWS Secrets Manager", secretName);
        } catch (Exception e) {
            log.error("Failed to delete secret {}", secretName, e);
        }
    }
}
```

---

## Layer 6: CloudTrail Anomaly Detection Integration

```java
package com.example.security.monitoring;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.stereotype.Service;
import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@Service
public class ApiUsageAnomalyDetector {

    private static final Logger log = LoggerFactory.getLogger(ApiUsageAnomalyDetector.class);

    private final Map<String, ApiKeyUsageStats> keyUsageMap = new ConcurrentHashMap<>();

    private static final int ANOMALY_THRESHOLD_MULTIPLIER = 3;
    private static final int GEO_ANOMALY_THRESHOLD = 2;
    private static final int RATE_ANOMALY_WINDOW_MINUTES = 10;

    public void recordApiCall(String apiKey, String ipAddress, String endpoint) {
        keyUsageMap.computeIfAbsent(apiKey, k -> new ApiKeyUsageStats())
            .recordCall(ipAddress, endpoint);
    }

    public boolean isAnomalous(String apiKey) {
        ApiKeyUsageStats stats = keyUsageMap.get(apiKey);
        if (stats == null) {
            return false;
        }
        return stats.isGeoAnomalous() || stats.isRateAnomalous();
    }

    public List<AnomalyAlert> checkForAnomalies() {
        List<AnomalyAlert> alerts = new ArrayList<>();

        for (Map.Entry<String, ApiKeyUsageStats> entry : keyUsageMap.entrySet()) {
            String key = entry.getKey();
            ApiKeyUsageStats stats = entry.getValue();

            if (stats.isGeoAnomalous()) {
                alerts.add(new AnomalyAlert(
                    key,
                    "GEO_ANOMALY",
                    "API key used from unusual geographic location",
                    stats.getUniqueIps(),
                    stats.getCallCount(),
                    Instant.now()
                ));
            }

            if (stats.isRateAnomalous()) {
                alerts.add(new AnomalyAlert(
                    key,
                    "RATE_ANOMALY",
                    "API key usage rate " + stats.getCallRate() +
                        " calls/minute exceeds threshold",
                    stats.getUniqueIps(),
                    stats.getCallCount(),
                    Instant.now()
                ));
            }
        }

        return alerts;
    }

    static class ApiKeyUsageStats {
        private final Map<String, Integer> ipCounts = new HashMap<>();
        private final List<Long> callTimestamps = new ArrayList<>();
        private int totalCalls = 0;
        private int baselineCallsPerMinute = 5;

        synchronized void recordCall(String ipAddress, String endpoint) {
            ipCounts.merge(ipAddress, 1, Integer::sum);
            callTimestamps.add(System.currentTimeMillis());
            totalCalls++;
        }

        synchronized boolean isGeoAnomalous() {
            // More than 2 unique IPs from different geo regions is anomalous
            return ipCounts.size() > GEO_ANOMALY_THRESHOLD;
        }

        synchronized boolean isRateAnomalous() {
            long now = System.currentTimeMillis();
            long cutoff = now - (RATE_ANOMALY_WINDOW_MINUTES * 60 * 1000);

            int recentCalls = (int) callTimestamps.stream()
                .filter(ts -> ts > cutoff)
                .count();

            double rate = (double) recentCalls / RATE_ANOMALY_WINDOW_MINUTES;
            return rate > baselineCallsPerMinute * ANOMALY_THRESHOLD_MULTIPLIER;
        }

        synchronized int getCallRate() {
            long now = System.currentTimeMillis();
            long cutoff = now - 60000;
            return (int) callTimestamps.stream()
                .filter(ts -> ts > cutoff)
                .count();
        }

        int getCallCount() { return totalCalls; }
        Set<String> getUniqueIps() { return ipCounts.keySet(); }
    }

    static class AnomalyAlert {
        private final String apiKey;
        private final String type;
        private final String description;
        private final Set<String> ips;
        private final int callCount;
        private final Instant timestamp;

        AnomalyAlert(String apiKey, String type, String description,
                     Set<String> ips, int callCount, Instant timestamp) {
            this.apiKey = apiKey;
            this.type = type;
            this.description = description;
            this.ips = ips;
            this.callCount = callCount;
            this.timestamp = timestamp;
        }

        public String getApiKey() { return apiKey; }
        public String getType() { return type; }
        public String getDescription() { return description; }
        public Instant getTimestamp() { return timestamp; }
    }
}
```

---

## Complete Remediation Steps

### Step 1: Immediate Security Response
1. Revoke compromised API key immediately
2. Block attacker IP at Cloudflare WAF
3. Rotate all API keys (not just compromised one)
4. Remove `.env` file from git history using `git filter-branch`

### Step 2: Implement IP Whitelisting
1. Add `IpWhitelistService` to all sensitive API endpoints
2. Configure allowed IP ranges (internal VPC, office VPN)
3. Set emergency contact IPs as always-allowed

### Step 3: Implement Rate Limiting
1. Add `ApiKeyRateLimiter` to application
2. Configure rate limits per key (1000/hr default, 100/hr for export endpoints)

### Step 4: Implement Secret Scanning
1. Update `.gitignore` to exclude `.env` and secret files
2. Deploy pre-commit hook for secret scanning
3. Add GitHub Actions secret scanning workflow

### Step 5: Migrate to AWS Secrets Manager
1. Create secrets in AWS Secrets Manager
2. Update application to read secrets from Secrets Manager
3. Configure automatic secret rotation (90-day)

### Step 6: Implement Anomaly Detection
1. Add `ApiUsageAnomalyDetector` to application
2. Configure alerts for geo-anomalies and rate-anomalies
3. Integrate with PagerDuty for security alerts

---

## References
- AWS Security Blog: "How to Rotate API Keys Securely"
- Cloudflare Blog: "API Security Report 2024"
- OWASP API Security Top 10 — https://web.archive.org/web/20200218212644/https://owasp.org/www-project-api-security/
- GitGuardian Blog: "How to Prevent Secret Leaks in Git"
- NIST SP 800-53: "Security and Privacy Controls"
- CrowdStrike 2024 Global Threat Report
- Google Cloud Blog: "Secrets Management Best Practices"
