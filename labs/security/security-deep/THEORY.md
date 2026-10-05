# Theory: security-deep

## Core Concepts

### Advanced Security Engineering

Security Deep Academy covers the full spectrum of modern security engineering, from cryptographic primitives to organizational security architecture.

### Key Principles

1. **Defense in Depth** — Multiple overlapping controls so a single failure never compromises the system.
2. **Least Privilege** — Every process, user, and service operates with the minimum permissions required.
3. **Zero Trust** — Never trust, always verify; assume breach and validate every request.
4. **Shift Left** — Integrate security testing early in the development lifecycle.
5. **Fail Secure** — Systems default to a denied state on failure.

### Cryptography Deep

- **Symmetric Encryption**: AES-256-GCM provides confidentiality + authenticity; key management is the hard part.
- **Asymmetric Encryption**: RSA-2048+ and ECC (P-256, P-384) enable key exchange and digital signatures.
- **Key Exchange**: Diffie-Hellman (DH) and ECDH allow two parties to establish a shared secret over an insecure channel.
- **Digital Signatures**: ECDSA and RSA-PSS provide non-repudiation and integrity.
- **Hashing**: SHA-256/SHA-3 for integrity; Argon2id/bcrypt for password hashing.

### OAuth2 & OIDC

- **Authorization Code + PKCE** is the gold standard for public clients.
- **Client Credentials** for machine-to-machine communication.
- **Token Validation**: Always verify signature, issuer, audience, and expiration.
- **Refresh Token Rotation** limits the blast radius of token theft.

### Penetration Testing Methodology

1. **Reconnaissance** — Passive and active information gathering.
2. **Scanning & Enumeration** — Port scanning, service identification, vulnerability mapping.
3. **Exploitation** — Controlled attacks to validate vulnerabilities.
4. **Post-Exploitation** — Privilege escalation, lateral movement, data access.
5. **Reporting** — Risk-rated findings with remediation guidance.

### SAST & DAST

- **SAST** analyzes source code for vulnerabilities without executing it; fast but can produce false positives.
- **DAST** tests running applications from the outside; finds runtime issues but misses logic flaws.
- **IAST** combines both approaches with runtime instrumentation.

### Container Security

- **Image Scanning**: Trivy, Grype, Snyk for CVE detection in base images and dependencies.
- **Runtime Security**: Falco, Sysdig for anomaly detection in running containers.
- **Pod Security**: Kubernetes Pod Security Standards (restricted profile), network policies, RBAC.
- **Supply Chain**: Sign images with Cosign, verify with Sigstore.

### API Security

- **OWASP API Top 10**: Broken object level authorization, broken authentication, excessive data exposure.
- **Rate Limiting**: Token bucket, sliding window algorithms to prevent abuse.
- **Input Validation**: Schema validation, parameterized queries, output encoding.

### Identity Management

- **SSO**: SAML 2.0, OIDC for cross-domain authentication.
- **LDAP/AD**: Directory services for enterprise identity storage.
- **SCIM**: System for Cross-domain Identity Management for user provisioning.
- **MFA**: TOTP, WebAuthn/FIDO2, push notifications.

### Zero Trust Architecture

- **Micro-segmentation**: Network isolation at the workload level.
- **Continuous Verification**: Re-authenticate and re-authorize continuously.
- **BeyondCorp**: Google's implementation of zero trust for enterprise access.
- **Identity-Aware Proxies**: Per-request authorization decisions.

## Detailed Analysis

### Why Deep Security Matters

Surface-level security knowledge is insufficient for modern threats. Deep understanding of cryptographic primitives, protocol internals, and attack methodologies enables engineers to design systems that withstand sophisticated adversaries.

### Java Platform Security

- **JCA/JCE**: Java Cryptography Architecture for pluggable cryptographic providers.
- **JAAS**: Java Authentication and Authorization Service for pluggable authentication.
- **Spring Security**: Filter-chain architecture for web application security.
- **Bouncy Castle**: Comprehensive cryptographic library for Java.

### Threat Modeling

Apply STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege) to systematically identify threats and design mitigations.
