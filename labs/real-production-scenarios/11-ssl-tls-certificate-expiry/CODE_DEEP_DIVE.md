# Lab 11 — Code Deep Dive: openssl + cert-manager Runbook

## 1. Confirm Expiry in <2 Minutes
```bash
# Live cert dates + chain
echo | openssl s_client -connect api.example.com:443 -servername api.example.com 2>/dev/null | openssl x509 -noout -dates -subject -issuer
# Full chain
openssl s_client -connect api.example.com:443 -showcerts </dev/null | grep -E "s:|i:|Not After"
# Days left (Linux)
END=$(date -d "$(echo | openssl s_client -connect api.example.com:443 -servername api.example.com 2>/dev/null | openssl x509 -noout -enddate | cut -d= -f2)" +%s); echo $(( (END - $(date +%s)) / 86400 ))" days left"
# OCSP stapling
openssl s_client -connect api.example.com:443 -status </dev/null 2>&1 | grep -A2 OCSP
```

## 2. cert-manager Triage
```bash
kubectl get certificate -A
kubectl describe certificate api-tls -n prod
kubectl get certificaterequest -n prod --sort-by=.metadata.creationTimestamp
kubectl describe order challenge -n prod | tail -40
kubectl get events -n prod --sort-by=.lastTimestamp | grep -i -E "cert|issu|fail"
kubectl get secret api-tls -n prod -o jsonpath='{.data.tls\.crt}' | base64 -d | openssl x509 -noout -dates
```

## 3. Log Snippets (What Expired Looks Like)
```
# nginx ingress
2026/10/05 SSL: error:0A000086:SSL routines::certificate verify failed (certificate has expired)
# Java service
javax.net.ssl.SSLHandshakeException: PKIX path validation failed: java.security.cert.CertPathValidatorException: validity check failed
Caused by: java.security.cert.CertificateExpiredException: NotAfter: Sun Oct 04 12:00:00 UTC 2026
# cert-manager
Warning Failed Issuing failed: ACME challenge failed: DNS problem: NXDOMAIN looking up TXT _acme-challenge.api.example.com
Normal RenewalScheduled Renewing in 29d
```

## 4. Emergency Mitigation
```bash
# Option A: force renewal
kubectl annotate certificate api-tls -n prod cert-manager.io/revision-history-limit- || true
cmctl renew api-tls -n prod   # cert-manager CLI
# Option B: apply fallback cert secret (pre-staged)
kubectl rollout restart deploy/api -n prod
# Verify
curl -sv https://api.example.com/health 2>&1 | grep -E "subject|expire|SSL certificate"
```

## 5. Java Truststore Check
```bash
keytool -list -v -keystore $JAVA_HOME/lib/security/cacerts -storepass changeit | grep -A2 "Alias\|Valid"
# Spring Boot: trigger SSL bundle reload (Actuator) or rolling restart
curl -X POST http://localhost:8080/actuator/restart
```

## 6. Prometheus Alerts
```yaml
- alert: CertExpiringSoon
  expr: (certmanager_certificate_expiration_timestamp_seconds - time()) < 14*24*3600
  labels: {severity: warning}
- alert: CertExpiringCritical
  expr: (certmanager_certificate_expiration_timestamp_seconds - time()) < 7*24*3600
  labels: {severity: critical}
```

Runbook order: confirm → check cert-manager events → force renew or fallback → verify → comms → post-mortem.
