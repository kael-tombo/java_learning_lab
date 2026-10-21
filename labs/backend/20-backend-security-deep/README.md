# Lab 20: Backend Security Deep Dive

## Overview
Advanced security topics: CSRF protection, CORS configuration, rate limiting, input validation, SQL injection prevention, and secure coding practices.

## Topics Covered
- CSRF attacks and prevention (synchronizer token, same-site cookies)
- CORS configuration best practices
- Rate limiting strategies (token bucket, sliding window)
- Input validation and sanitization
- SQL injection prevention (parameterized queries, ORM safety)
- XSS prevention (output encoding, CSP headers)
- Secure HTTP headers (HSTS, X-Frame-Options, X-Content-Type-Options)
- Dependency vulnerability scanning

## Prerequisites
- Java 21+
- Spring Boot 3.3+
- Basic security concepts

## Key Dependencies
`xml
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-security</artifactId>
</dependency>
<dependency>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-validation</artifactId>
</dependency>
<dependency>
    <groupId>org.owasp.encoder</groupId>
    <artifactId>encoder</artifactId>
    <version>1.2.3</version>
</dependency>
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\20-backend-security-deep "THEORY.md") @"
# Theory: Backend Security Deep Dive

## 1. CSRF (Cross-Site Request Forgery)

CSRF tricks a user into executing unwanted actions on an authenticated site. Prevention:
- Synchronizer token pattern: Include CSRF token in forms
- SameSite cookies: Set SameSite=Strict/Lax
- Double-submit cookie: Match cookie and header values
- Custom request headers: Required for state-changing operations

## 2. CORS (Cross-Origin Resource Sharing)

CORS controls which origins can access your API:
- Access-Control-Allow-Origin: Allowed origins
- Access-Control-Allow-Methods: Allowed HTTP methods
- Access-Control-Allow-Headers: Allowed headers
- Access-Control-Allow-Credentials: Whether cookies are sent
- Access-Control-Max-Age: Preflight cache duration

## 3. Rate Limiting

Prevent abuse by limiting requests:
- Token Bucket: Tokens refill at fixed rate, each request consumes one
- Sliding Window: Track requests in time window
- Leaky Bucket: Queue requests and process at fixed rate
- Fixed Window: Reset counter after time window

## 4. Input Validation

Defense-in-depth for user input:
- Whitelist validation (accept known good)
- Blacklist validation (reject known bad)
- Bean Validation (@NotNull, @Size, @Pattern)
- Custom validators for business rules

## 5. SQL Injection Prevention

Never concatenate user input into SQL:
- Use parameterized queries (PreparedStatement)
- Use JPA/Hibernate (avoid native queries with user input)
- Use query criteria API
- Validate and sanitize input
- Use stored procedures with parameters

## 6. XSS Prevention

Cross-Site Scripting prevention:
- Output encoding (HTML, JavaScript, URL context)
- Content Security Policy headers
- Context-aware escaping (OWASP Encoder)
- X-XSS-Protection header
- Avoid dangerouslySetInnerHTML (React) / unescaped output (JSP/Thymeleaf)

## 7. Secure Headers

- Strict-Transport-Security: Enforce HTTPS
- X-Frame-Options: DENY/SAMEORIGIN (clickjacking)
- X-Content-Type-Options: nosniff (MIME sniffing)
- Content-Security-Policy: Load resources only from trusted sources
- Referrer-Policy: Control referrer header
- Permissions-Policy: Restrict browser features
