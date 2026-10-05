# Mini Project: security-deep

## Project: SecureVault API

Build a secure REST API that demonstrates all concepts from the Security Deep Academy micro-labs.

## Overview

SecureVault is a password vault API that allows users to store, retrieve, and manage encrypted credentials. It implements defense-in-depth with multiple security layers.

## Tech Stack

- **Java 17+** with Spring Boot 3.x
- **Spring Security** with JWT authentication
- **PostgreSQL** for data storage
- **Redis** for rate limiting and session management
- **Docker** for containerization

## Project Structure

```
secure-vault-api/
├── src/main/java/com/security/deep/
│   ├── SecureVaultApplication.java
│   ├── config/
│   │   ├── SecurityConfig.java
│   │   ├── RateLimitConfig.java
│   │   └── JwtConfig.java
│   ├── controller/
│   │   ├── AuthController.java
│   │   ├── VaultController.java
│   │   └── HealthController.java
│   ├── service/
│   │   ├── JwtService.java
│   │   ├── VaultService.java
│   │   ├── EncryptionService.java
│   │   └── RateLimiterService.java
│   ├── model/
│   │   ├── User.java
│   │   ├── VaultEntry.java
│   │   └── dto/
│   ├── repository/
│   │   ├── UserRepository.java
│   │   └── VaultEntryRepository.java
│   └── security/
│       ├── JwtAuthenticationFilter.java
│       ├── RateLimitFilter.java
│       └── AuditLogger.java
├── src/main/resources/
│   ├── application.yml
│   └── schema.sql
├── Dockerfile
├── docker-compose.yml
└── pom.xml
```

## Requirements

### 1. Authentication & Authorization

- [ ] User registration with email verification
- [ ] Login with JWT access + refresh tokens
- [ ] Refresh token rotation with reuse detection
- [ ] Role-based access control (USER, ADMIN)
- [ ] Account lockout after 5 failed attempts
- [ ] Password strength validation (zxcvbn or similar)

### 2. Encryption

- [ ] AES-256-GCM for vault entry encryption
- [ ] Per-user encryption keys derived from master key + user salt
- [ ] Argon2id for password hashing
- [ ] Secure key storage (environment variables, not code)

### 3. API Security

- [ ] Rate limiting: 100 requests/minute per user
- [ ] Input validation on all endpoints
- [ ] CORS configuration (whitelist origins only)
- [ ] Security headers (HSTS, CSP, X-Frame-Options, etc.)
- [ ] HTTPS only (redirect HTTP to HTTPS)

### 4. Audit & Monitoring

- [ ] Log all authentication events
- [ ] Log all vault access (read/write/delete)
- [ ] Structured logging (JSON format)
- [ ] Health check endpoint with security status

### 5. Container Security

- [ ] Multi-stage Dockerfile (build + runtime)
- [ ] Non-root user in container
- [ ] Read-only root filesystem
- [ ] Minimal base image (distroless or alpine)
- [ ] Image scanning with Trivy

## API Endpoints

### Auth
```
POST /api/auth/register    - Register new user
POST /api/auth/login       - Login, returns JWT
POST /api/auth/refresh     - Refresh access token
POST /api/auth/logout      - Invalidate refresh token
```

### Vault
```
GET    /api/vault          - List all entries (metadata only)
POST   /api/vault          - Create new entry
GET    /api/vault/{id}     - Get decrypted entry
PUT    /api/vault/{id}     - Update entry
DELETE /api/vault/{id}     - Delete entry
```

### Admin
```
GET    /api/admin/users    - List all users (ADMIN only)
DELETE /api/admin/users/{id} - Delete user (ADMIN only)
```

## Implementation Steps

### Step 1: Project Setup
1. Create Spring Boot project with Spring Security, JPA, Web dependencies
2. Configure PostgreSQL connection
3. Set up Redis for rate limiting

### Step 2: Authentication
1. Implement User entity and repository
2. Create JWT service with access + refresh tokens
3. Implement authentication filter
4. Add refresh token rotation

### Step 3: Encryption
1. Implement AES-256-GCM encryption service
2. Create key derivation function
3. Integrate encryption into vault operations

### Step 4: API Security
1. Add rate limiting filter
2. Configure CORS and security headers
3. Add input validation
4. Implement audit logging

### Step 5: Containerization
1. Write multi-stage Dockerfile
2. Create docker-compose.yml
3. Add Trivy scanning to build process

## Testing

### Unit Tests
- [ ] JWT service tests
- [ ] Encryption service tests
- [ ] Rate limiter tests

### Integration Tests
- [ ] Authentication flow tests
- [ ] Vault CRUD operations
- [ ] Rate limiting behavior
- [ ] Authorization checks

### Security Tests
- [ ] SQL injection attempts
- [ ] XSS payload tests
- [ ] JWT tampering tests
- [ ] Rate limit bypass attempts

## Success Criteria

- [ ] All endpoints functional and documented
- [ ] All security controls implemented
- [ ] Test coverage > 80%
- [ ] Trivy scan: 0 critical vulnerabilities
- [ ] OWASP ZAP baseline scan: 0 high/critical alerts
- [ ] Code review passed

## Bonus Challenges

1. **WebAuthn Support**: Add passkey authentication
2. **Zero Trust**: Implement continuous verification
3. **SIEM Integration**: Send logs to ELK stack
4. **Kubernetes**: Deploy with Helm chart and network policies
