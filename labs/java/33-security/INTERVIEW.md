# Interview Questions: Security

## Company-Specific Focus

### Google
- Java Security Manager: legacy vs modern approach
- Cryptography: Cipher, MessageDigest, Signature, KeyStore
- Secure coding OWASP guidelines in Java

### Microsoft
- Java vs C# security: how each handles cryptography and permissions
- Secret management in Azure: using KeyVault from Java
- Authentication: JWT, OAuth 2.0 with Java libraries

### Amazon
- IAM and Java SDK: signing requests with AWS SigV4
- TLS mutual authentication in microservices
- KMS integration via the SDK

### Meta
- Input validation: preventing XSS, SQL injection in Java
- Using PreparedStatement to prevent injection
- Encryption at rest vs in transit

### Apple
- Platform security: keychain on macOS with Java
- Avoiding system.exit() due to security manager policy
- Constant-time string comparison for security

### Oracle
- The Java security architecture
- JCA (Java Cryptography Architecture) and JCE (Java Cryptography Extension)
- The Security Manager and legacy
- signed jars and the Java plugin

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| 535 Encode and Decode TinyURL | Medium | Google, Amazon, Apple | Input validation and sanitization |
| 168 Excel Sheet Column Title | Easy | Amazon, Google, Apple | Secure string construction |
| 43 Multiply Strings | Medium | Amazon, Google, Apple | Input validation |
| 8 String to Integer (atoi) | Medium | Amazon, Google | Validate input boundaries |
| 65 Valid Number | Hard | Amazon, Google, Microsoft | Input validation patterns |

## Real Production Scenarios
- **Equifax**: Apache Struts vulnerability allowed RCE due to insufficient input validation
- **Cloudflare**: Private keys leaked via memory dumps because of not zeroing out char[]
- **GitHub**: Use of `WeakHashMap` for user sessions resulting in credential theft

## Interview Patterns & Tips
- **Use PreparedStatement**: Never use string concatenation for SQL queries.
- **Use char[] for passwords**: Allows explicit overwriting; String is immutable.
- **Validate and sanitize**: All user input must be validated on the server side.
- **Use TLS**: All socket communication should use TLS.

## Deep Dive Questions
- **JCA**: How does the Provider architecture work?
- **SecureRandom**: Difference between SHA1PRNG and NativePRNG?
- **TLS**: How does the JSSE implementation handle handshaking?
- **KeyStore**: What types of keystores exist? (JKS, PKCS12)
- **Module System**: How does the module system harden security boundaries?