# Exercises: security-deep

## Cryptography Deep

### Exercise 1: Implement AES-256-GCM Encryption

Create a Java utility class that encrypts and decrypts data using AES-256-GCM.

**Requirements:**
- Generate a random 256-bit key
- Use a 96-bit IV (nonce) for each encryption
- Include authentication tag (128-bit)
- Handle ciphertext + IV concatenation for storage

**Starter:**
```java
public class AESGCM {
    private static final int GCM_IV_LENGTH = 12;
    private static final int GCM_TAG_LENGTH = 16;
    
    public static byte[] encrypt(byte[] plaintext, byte[] key) { ... }
    public static byte[] decrypt(byte[] ciphertext, byte[] key) { ... }
}
```

### Exercise 2: Implement RSA Key Pair Generation and Signing

Generate an RSA-2048 key pair, sign a message with the private key, and verify with the public key.

**Requirements:**
- Use `KeyPairGenerator` with RSA/2048
- Sign using SHA256withRSA
- Verify signature and handle `SignatureException`

### Exercise 3: Implement ECDH Key Exchange

Simulate two parties establishing a shared secret using Elliptic Curve Diffie-Hellman.

**Requirements:**
- Use `KeyAgreement` with `EC` algorithm
- Both parties generate key pairs
- Derive identical shared secrets
- Use the shared secret as an AES key

### Exercise 4: Password Hashing with Argon2id

Implement password hashing and verification using Argon2id via Bouncy Castle.

**Requirements:**
- Configure memory, iterations, and parallelism parameters
- Store salt with the hash
- Implement constant-time comparison for verification

## OAuth2 & OIDC

### Exercise 5: Build an Authorization Code Flow

Implement a minimal OAuth2 authorization code flow with PKCE.

**Requirements:**
- Generate code verifier and challenge (S256)
- Redirect to authorization endpoint
- Exchange code for tokens at token endpoint
- Validate ID token (OIDC)

### Exercise 6: JWT Token Validation

Write a JWT validator that checks signature, issuer, audience, and expiration.

**Requirements:**
- Parse JWT header and payload
- Verify signature using JWKS endpoint
- Validate `iss`, `aud`, `exp`, `nbf` claims
- Handle clock skew with leeway

### Exercise 7: Refresh Token Rotation

Implement refresh token rotation with reuse detection.

**Requirements:**
- Issue new refresh token on each use
- Detect reuse of old refresh token
- Revoke entire token family on reuse
- Implement sliding expiration

## Penetration Testing

### Exercise 8: Port Scanner

Build a TCP connect port scanner in Java.

**Requirements:**
- Scan a range of ports on a target host
- Use `Socket` with timeout for each port
- Identify open ports and attempt banner grabbing
- Implement multi-threading for speed

### Exercise 9: SQL Injection Detection

Create a tool that tests endpoints for SQL injection vulnerabilities.

**Requirements:**
- Send payloads like `' OR '1'='1` and `'; DROP TABLE--`
- Analyze responses for error-based detection
- Test time-based blind injection with `SLEEP()`
- Generate a vulnerability report

### Exercise 10: Vulnerability Report Generator

Write a program that takes scan results and generates a structured vulnerability report.

**Requirements:**
- Classify findings by severity (Critical/High/Medium/Low)
- Include CVSS scoring
- Provide remediation guidance
- Output in Markdown format

## SAST & DAST

### Exercise 11: Integrate SpotBugs into Maven

Configure SpotBugs with security plugin in a Maven project.

**Requirements:**
- Add `spotbugs-maven-plugin` with `findsecbugs-plugin`
- Run analysis and interpret results
- Suppress false positives with annotations
- Fail build on critical findings

### Exercise 12: OWASP ZAP Baseline Scan

Run an OWASP ZAP baseline scan against a running application.

**Requirements:**
- Start ZAP in daemon mode
- Configure spider and active scan
- Generate HTML report
- Parse alerts for actionable findings

## Container Security

### Exercise 13: Dockerfile Security Audit

Write a script that audits Dockerfiles for security best practices.

**Requirements:**
- Check for non-root user
- Detect hardcoded secrets
- Verify minimal base images
- Flag unnecessary packages

### Exercise 14: Kubernetes Pod Security Policy

Create a Kubernetes Pod Security Policy that enforces restricted standards.

**Requirements:**
- Disallow privileged containers
- Require read-only root filesystem
- Restrict host namespaces
- Limit capabilities

## API Security

### Exercise 15: Rate Limiter Implementation

Implement a token bucket rate limiter for a Spring Boot API.

**Requirements:**
- Configurable requests per second per client
- Use `ConcurrentHashMap` for client tracking
- Return 429 Too Many Requests when exceeded
- Add `X-RateLimit-*` headers

### Exercise 16: Input Validation Framework

Build a reusable input validation framework.

**Requirements:**
- Annotation-based validation (`@SafeInput`, `@Email`, `@URL`)
- Schema validation for JSON payloads
- Output encoding for HTML contexts
- Integration with Spring Validator

## Identity Management

### Exercise 17: SAML SSO Integration

Configure a Spring Boot application as a SAML Service Provider.

**Requirements:**
- Generate SP metadata
- Configure IdP metadata
- Handle SAML assertions
- Map SAML attributes to user details

### Exercise 18: SCIM User Provisioning

Implement a SCIM 2.0 endpoint for user provisioning.

**Requirements:**
- Support `GET /Users`, `POST /Users`, `PATCH /Users`
- Implement filtering with `filter` query parameter
- Return proper SCIM error responses
- Handle pagination with `startIndex` and `count`

## Zero Trust

### Exercise 19: Identity-Aware Proxy

Build a simple identity-aware proxy that validates JWTs before forwarding requests.

**Requirements:**
- Extract JWT from `Authorization` header
- Validate signature and claims
- Forward only authenticated requests
- Add user identity headers to upstream

### Exercise 20: Micro-segmentation Policy Engine

Design a policy engine for micro-segmentation decisions.

**Requirements:**
- Define policies in YAML/JSON
- Evaluate policies based on identity, device posture, and context
- Default-deny with explicit allow rules
- Log all decisions for audit
