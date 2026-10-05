# Quiz: security-deep

## Cryptography

**Q1:** What is the recommended symmetric encryption mode for authenticated encryption?
- A) ECB
- B) CBC
- C) GCM
- D) OFB

**Answer:** C) GCM — AES-GCM provides both confidentiality and authenticity.

**Q2:** Which key size is considered the minimum for RSA in 2026?
- A) 1024
- B) 2048
- C) 4096
- D) 512

**Answer:** B) 2048 — NIST recommends 2048-bit minimum for RSA through 2030.

**Q3:** What is the primary advantage of ECC over RSA?
- A) Faster encryption speed
- B) Smaller key sizes for equivalent security
- C) Easier to implement
- D) No need for key exchange

**Answer:** B) Smaller key sizes — 256-bit ECC ≈ 3072-bit RSA in security strength.

## OAuth2 & OIDC

**Q4:** What does PKCE protect against?
- A) CSRF
- B) Authorization code interception
- C) Token theft
- D) Phishing

**Answer:** B) Authorization code interception — PKCE binds the code to the client that requested it.

**Q5:** Which OAuth2 flow is recommended for server-side web applications?
- A) Implicit
- B) Resource Owner Password Credentials
- C) Authorization Code
- D) Client Credentials

**Answer:** C) Authorization Code — with PKCE for public clients.

**Q6:** What is the purpose of the `nonce` claim in an OIDC ID token?
- A) Prevent token replay
- B) Prevent CSRF
- C) Bind token to session
- D) All of the above

**Answer:** D) All of the above — nonce provides replay protection and session binding.

## Penetration Testing

**Q7:** What is the first phase of a penetration test?
- A) Exploitation
- B) Reconnaissance
- C) Reporting
- D) Scanning

**Answer:** B) Reconnaissance — gathering information about the target.

**Q8:** What does a "false positive" mean in vulnerability scanning?
- A) A vulnerability that was missed
- B) A reported vulnerability that is not actually exploitable
- C) A critical vulnerability
- D) A vulnerability in the scanner itself

**Answer:** B) A reported vulnerability that is not actually exploitable.

## SAST & DAST

**Q9:** What is the main advantage of SAST over DAST?
- A) Finds more vulnerabilities
- B) Can analyze code without running it
- C) Tests runtime behavior
- D) No false positives

**Answer:** B) Can analyze code without running it — SAST works on source code.

**Q10:** Which tool is commonly used for DAST?
- A) SpotBugs
- B) SonarQube
- C) OWASP ZAP
- D) Checkmarx

**Answer:** C) OWASP ZAP — it tests running applications.

## Container Security

**Q11:** What is the purpose of a read-only root filesystem in containers?
- A) Improve performance
- B) Prevent attackers from writing malicious files
- C) Reduce image size
- D) Enable faster startup

**Answer:** B) Prevent attackers from writing malicious files — limits post-exploitation.

**Q12:** Which tool is used for container image vulnerability scanning?
- A) Trivy
- B) Jenkins
- C) Terraform
- D) Ansible

**Answer:** A) Trivy — scans images for CVEs in OS packages and dependencies.

## API Security

**Q13:** What is the #1 API security risk per OWASP?
- A) Broken authentication
- B) Broken object level authorization
- C) Excessive data exposure
- D) Rate limiting

**Answer:** B) Broken object level authorization — BOLA is the most critical API risk.

**Q14:** What HTTP status code should a rate-limited API return?
- A) 403
- B) 429
- C) 503
- D) 401

**Answer:** B) 429 Too Many Requests.

## Identity Management

**Q15:** What does SCIM stand for?
- A) Secure Cross-domain Identity Management
- B) System for Cross-domain Identity Management
- C) Standard Cross-domain Identity Mechanism
- D) Secure Cloud Identity Management

**Answer:** B) System for Cross-domain Identity Management.

**Q16:** Which protocol is preferred for modern SSO implementations?
- A) SAML 1.1
- B) OAuth2/OIDC
- C) LDAP
- D) Kerberos

**Answer:** B) OAuth2/OIDC — modern, JSON-based, and extensible.

## Zero Trust

**Q17:** What is the core principle of Zero Trust?
- A) Trust but verify
- B) Never trust, always verify
- C) Trust internal networks
- D) Verify once, trust forever

**Answer:** B) Never trust, always verify — every request is authenticated and authorized.

**Q18:** What is micro-segmentation?
- A) Dividing the network into small subnets
- B) Isolating workloads with granular network policies
- C) Using microservices architecture
- D) Segmenting by geographic region

**Answer:** B) Isolating workloads with granular network policies — limits lateral movement.

## Scoring

- 15-18 correct: Security expert — ready for advanced red team work
- 10-14 correct: Strong foundation — review missed topics
- 5-9 correct: Intermediate — revisit theory sections
- 0-4 correct: Beginner — start with the micro-labs in order
