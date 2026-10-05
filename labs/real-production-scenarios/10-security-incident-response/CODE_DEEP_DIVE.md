# CODE DEEP DIVE — Lab 10: Security Runbook

## 1. Scope + Revoke
```bash
kubectl audit-log... # cloud audit:
kubectl auth can-i --list --as=suspect-user
# IdP: list sessions/tokens for user, revoke all
curl -s -H "Authorization: Bearer OLD_TOKEN" https://api.example.com/me -w "%{http_code}\n"
# expect 401 after revoke
# log snippet:
# WARN auth: impossible-travel user=b.obasi ip1=41.90.64.2 ip2=185.220.70.4 dt=8m
# WARN auth: admin path 403->200 flip /admin/export by svc-account-X
```

## 2. Isolate Workload
```bash
kubectl label pod bad-pod-xyz quarantine=true --overwrite
kubectl scale deployment compromised-app --replicas=0 -n prod
```
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata: { name: quarantine-deny-all, namespace: prod }
spec: { podSelector: { matchLabels: { quarantine: "true" } }, policyTypes: [Ingress, Egress] }
```

## 3. JWT Fix (Java)
```java
JwtDecoder dec = NimbusJwtDecoder.withJwkSetUri(jwks).build();
dec.setJwtValidator(new DelegatingOAuth2TokenValidator<>(
  new JwtTimestampValidator(), new JwtIssuerValidator(issuer),
  new JwtClaimValidator<List<String>>("aud", aud::equals)));
// reject alg:none by allowlisting RS256 at parser config
```

## 4. TLS Verify + Rotate
```bash
echo | openssl s_client -connect api.example.com:443 -servername api.example.com 2>/dev/null | openssl x509 -noout -dates -issuer
curl -v https://api.example.com/health 2>&1 | grep -E "subject|expire|SSL"
```

## 5. Image Rebuild Clean
```bash
trivy image myapp:old | head -20
docker build -t myapp:patched .
trivy image myapp:patched | grep -i critical
cosign sign myapp:patched
```

## 6. curl Verify After Fix
```bash
curl -s -o /dev/null -w "%{http_code}\n" https://api.example.com/me -H "Authorization: Bearer NEW_TOKEN"
curl -m5 http://malicious-ioc.example/ --max-time 5; echo exit=$?
```

## 7. Anti-Patterns
- Only rotating password; editing prod by hand without snapshot; blocking /24 of a CDN and breaking legit traffic.
