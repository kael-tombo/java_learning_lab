# Visual Guide: Security

`
Attack → [WAF] → [Rate Limit] → [CORS] → [Auth] → [CSRF] → [Validation] → [App]
                                                   →“
                                             [Parameterized SQL] → [DB]
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\20-backend-security-deep "DEBUGGING.md") @"
# Debugging: Security

1. Check Spring Security filter chain order
2. Verify CSRF token in request headers vs cookies
3. Check CORS preflight (OPTIONS) response headers
4. Review HTTP security headers in browser DevTools
5. Enable DEBUG logging for org.springframework.security
6. Test rate limiting with curl timing
7. Verify SQL logging shows parameterized values
