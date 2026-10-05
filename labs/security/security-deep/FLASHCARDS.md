# Flashcards: security-deep

## Cryptography

**Front:** What encryption mode provides both confidentiality and authenticity?
**Back:** AES-GCM (Galois/Counter Mode)

**Front:** What is the minimum recommended RSA key size for 2026?
**Back:** 2048 bits (NIST recommendation through 2030)

**Front:** Which password hashing algorithm is recommended by OWASP?
**Back:** Argon2id (fallback: bcrypt, scrypt, PBKDF2)

**Front:** What does ECDH stand for?
**Back:** Elliptic Curve Diffie-Hellman — key exchange protocol

**Front:** What is the key size equivalence of 256-bit ECC vs RSA?
**Back:** 256-bit ECC ≈ 3072-bit RSA

**Front:** What is a cryptographic nonce?
**Back:** A number used once — prevents replay attacks in encryption

**Front:** What is the purpose of a salt in password hashing?
**Back:** Prevents rainbow table attacks by making each hash unique

**Front:** Which Java class provides AES encryption?
**Back:** `javax.crypto.Cipher` with `AES/GCM/NoPadding`

## OAuth2 & OIDC

**Front:** What does PKCE stand for?
**Back:** Proof Key for Code Exchange — prevents authorization code interception

**Front:** Which OAuth2 flow is for machine-to-machine communication?
**Back:** Client Credentials flow

**Front:** What are the three parts of a JWT?
**Back:** Header, Payload, Signature

**Front:** What does OIDC add to OAuth2?
**Back:** Identity layer — ID tokens and userinfo endpoint

**Front:** What is refresh token rotation?
**Back:** Issuing a new refresh token on each use; old one is invalidated

**Front:** What claim in a JWT prevents replay attacks?
**Back:** `jti` (JWT ID) — unique token identifier

**Front:** What is the `aud` claim in a JWT?
**Back:** Audience — intended recipient of the token

**Front:** What is the `iss` claim in a JWT?
**Back:** Issuer — who created the token

## Penetration Testing

**Front:** What are the 5 phases of penetration testing?
**Back:** Reconnaissance, Scanning, Exploitation, Post-Exploitation, Reporting

**Front:** What is a false positive in vulnerability scanning?
**Back:** A reported vulnerability that is not actually exploitable

**Front:** What tool is commonly used for network scanning?
**Back:** Nmap

**Front:** What is SQL injection?
**Back:** Injecting malicious SQL via input fields to manipulate database queries

**Front:** What is the OWASP Top 10?
**Back:** The 10 most critical web application security risks

## SAST & DAST

**Front:** What does SAST stand for?
**Back:** Static Application Security Testing — analyzes source code

**Front:** What does DAST stand for?
**Back:** Dynamic Application Security Testing — tests running applications

**Front:** What is the main advantage of SAST?
**Back:** Finds vulnerabilities early in development without running the app

**Front:** What is the main advantage of DAST?
**Back:** Finds runtime vulnerabilities that static analysis misses

**Front:** Name two SAST tools.
**Back:** SpotBugs, SonarQube, Checkmarx, Semgrep

**Front:** Name two DAST tools.
**Back:** OWASP ZAP, Burp Suite, Acunetix, Netsparker

## Container Security

**Front:** What tool scans container images for vulnerabilities?
**Back:** Trivy, Grype, Snyk, Clair

**Front:** Why use a read-only root filesystem in containers?
**Back:** Prevents attackers from writing malicious files post-exploitation

**Front:** What is Kubernetes Pod Security Standards?
**Back:** Baseline, Restricted, and Privileged profiles for pod security

**Front:** What is Falco used for?
**Back:** Runtime security monitoring — detects anomalous container behavior

**Front:** What is image signing?
**Back:** Cryptographically signing container images to verify integrity (Cosign/Sigstore)

## API Security

**Front:** What is BOLA?
**Back:** Broken Object Level Authorization — #1 OWASP API risk

**Front:** What HTTP status code indicates rate limiting?
**Back:** 429 Too Many Requests

**Front:** What is the purpose of input validation?
**Back:** Ensure data conforms to expected format before processing

**Front:** What is a common API authentication mechanism?
**Back:** JWT Bearer tokens in Authorization header

## Identity Management

**Front:** What does SCIM stand for?
**Back:** System for Cross-domain Identity Management

**Front:** What is SAML used for?
**Back:** Single Sign-On (SSO) — exchanging authentication/authorization data

**Front:** What is LDAP?
**Back:** Lightweight Directory Access Protocol — directory service for identity storage

**Front:** What is MFA?
**Back:** Multi-Factor Authentication — requiring 2+ verification factors

**Front:** What is identity federation?
**Back:** Linking identities across multiple identity management systems

## Zero Trust

**Front:** What is the core principle of Zero Trust?
**Back:** Never trust, always verify — authenticate every request

**Front:** What is micro-segmentation?
**Back:** Isolating workloads with granular network policies to limit lateral movement

**Front:** What is BeyondCorp?
**Back:** Google's Zero Trust implementation — access based on identity and device posture

**Front:** What is an identity-aware proxy?
**Back:** A proxy that validates identity before forwarding requests to backend services

**Front:** What is continuous verification in Zero Trust?
**Back:** Re-authenticating and re-authorizing throughout a session, not just at login
