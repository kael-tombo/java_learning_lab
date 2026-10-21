# Common Mistakes: Security

1. Disabling CSRF for all endpoints (not just REST APIs)
2. CORS set to * with credentials (not allowed by spec)
3. Storing passwords in plaintext
4. Not validating on server side (relying only on client-side)
5. SQL string concatenation
6. Exposing stack traces in production
7. Missing security headers
8. Not rate limiting authentication endpoints
