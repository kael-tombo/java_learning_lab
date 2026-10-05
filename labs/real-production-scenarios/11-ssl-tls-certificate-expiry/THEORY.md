# Lab 11 — SSL/TLS Certificate Expiry — Theory: Mechanics + Detection

## 1. Why Certificates Expire (Mechanics)
- X.509 certificates carry `notBefore` / `notAfter`; clients reject connections past `notAfter`.
- Chain of trust: leaf → intermediate → root. Any expired link breaks TLS handshake.
- Typical lifetimes: Let's Encrypt 90 days, commercial 398 days max (CA/Browser Forum rule).
- Rotation failure modes: forgotten cron, ACME challenge failure, wrong secret mounted, clock skew.
- Java-specific: `SSLHandshakeException: PKIX path validation failed`, truststore (`cacerts`) stale.

## 2. TLS Handshake Failure Mechanics
1. ClientHello → ServerHello + Certificate message.
2. Client validates dates, hostname (SAN), chain signatures, revocation (OCSP/CRL).
3. On expiry: handshake aborts with `certificate_expired` alert (TLS code 45).
4. Impact: 100% traffic loss on affected domain; load balancer health checks fail; cascading retries.

## 3. Detection Strategies
| Layer | Signal | Tool |
|-------|--------|------|
| Proactive | Days-to-expiry < 30/14/7 | Prometheus `ssl_exporter`, cert-manager metrics |
| Synthetic | HTTPS probe fails | Blackbox exporter, Datadog Synthetics |
| Logs | `certificate has expired` in ingress/nginx | Loki / ELK alert |
| Client-side | Spike in TLS errors, 526 (Cloudflare) | APM, CDN analytics |
| Audit | Inventory of all certs + owners | Weekly report job |

## 4. cert-manager Architecture (K8s)
- `Issuer`/`ClusterIssuer` → `Certificate` CR → renews `Secret` automatically.
- Key fields: `spec.secretName`, `spec.dnsNames`, `spec.issuerRef`, `spec.renewBefore`.
- Events to watch: `Issuing`, `RenewalScheduled`, `Failed`.
- Prometheus metrics: `certmanager_certificate_expiration_timestamp_seconds`.

## 5. Monitoring Queries
```promql
# Seconds until expiry
certmanager_certificate_expiration_timestamp_seconds - time()
# Alert: < 14 days
(certmanager_certificate_expiration_timestamp_seconds - time()) < 1209600
# Blackbox probe
probe_ssl_earliest_cert_expiry - time() < 7*24*3600
```

## 6. Prevention Principles
- Automate renewal (ACME DNS-01 for wildcards), never manual CSR email chains.
- Alert at 30/14/7/1 days with escalating severity (ticket → page).
- Maintain cert inventory: domain, issuer, expiry, owner, environment.
- Test rotation in staging; verify truststore reload without restart (Spring Boot reload).
- Pin runbook to on-call dashboard; rehearse quarterly.

## 7. Java Service Checklist
- Use `keytool -list -v -keystore` to inspect; reload `SSLContext` on secret change.
- Avoid disabling verification (`TrustAll`) as workaround — creates security incident.
- Set readiness probe to fail on cert load error so pod is replaced, not serving bad TLS.

## 8. Key Takeaways
- Expiry is 100% preventable — it is a process failure, not bad luck.
- Detect at metric layer (days-to-expiry), not user-complaint layer.
- Automate + alert + inventory = on-call excellence.
