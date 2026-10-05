# Lab 11 — Quiz: SSL/TLS Certificate Expiry (15 Questions)

1. What fields define a certificate's validity window?
- [ ] A) notBefore / notAfter
- [ ] B) serialNumber / version
- [ ] C) SAN / CN only
- [ ] D) OCSP / CRL
> Answer: A

2. What TLS alert is sent on expired cert?
- [ ] A) 45 certificate_expired
- [ ] B) 40 handshake_failure
- [ ] C) 10 unexpected_message
- [ ] D) 80 internal_error
> Answer: A

3. Max lifetime for public certs per CA/B Forum?
- [ ] A) 398 days
- [ ] B) 825 days
- [ ] C) 90 days only
- [ ] D) 3 years
> Answer: A

4. Which cert-manager CR requests a cert?
- [ ] A) Certificate
- [ ] B) Deployment
- [ ] C) IngressClass
- [ ] D) SecretProvider
> Answer: A

5. Best proactive SLI for expiry?
- [ ] A) Days-to-expiry per cert
- [ ] B) CPU usage
- [ ] C) Request latency p99
- [ ] D) Pod restarts
> Answer: A

6. `openssl s_client -connect host:443` is used to:
- [ ] A) Inspect live cert chain/dates
- [ ] B) Renew certs
- [ ] C) Update DNS
- [ ] D) Restart pods
> Answer: A

7. Java error on expired cert?
- [ ] A) SSLHandshakeException / PKIX path validation failed
- [ ] B) OutOfMemoryError
- [ ] C) SQLException
- [ ] D) ClassNotFoundException
> Answer: A

8. Recommended alert thresholds?
- [ ] A) 30/14/7/1 days escalating
- [ ] B) Only at expiry
- [ ] C) Only yearly
- [ ] D) Never alert
> Answer: A

9. DNS-01 challenge is needed for:
- [ ] A) Wildcard certs
- [ ] B) IP certs only
- [ ] C) Self-signed certs
- [ ] D) SSH keys
> Answer: A

10. What does `renewBefore` do in cert-manager?
- [ ] A) Triggers early renewal window
- [ ] B) Deletes the secret
- [ ] C) Disables OCSP
- [ ] D) Scales pods
> Answer: A

11. Cloudflare error for expired origin cert?
- [ ] A) 526 Invalid SSL Certificate
- [ ] B) 404
- [ ] C) 429
- [ ] D) 503 only
> Answer: A

12. Why is TrustAll a bad workaround?
- [ ] A) Disables verification, enables MITM
- [ ] B) Slows handshake
- [ ] C) Increases cert lifetime
- [ ] D) Breaks DNS
> Answer: A

13. Which metric tracks expiry in cert-manager?
- [ ] A) certmanager_certificate_expiration_timestamp_seconds
- [ ] B) http_requests_total
- [ ] C) container_cpu_usage
- [ ] D) kafka_consumer_lag
> Answer: A

14. First detection layer should be:
- [ ] A) Metric (days-to-expiry), not user complaints
- [ ] B) Twitter mentions
- [ ] C) Support tickets only
- [ ] D) Quarterly audit only
> Answer: A

15. Blast radius is minimized by:
- [ ] A) Per-service certs + automated rotation
- [ ] B) One shared cert never rotated
- [ ] C) Disabling TLS
- [ ] D) Manual email CSR chain
> Answer: A

Scoring: 13–15 excellent, 10–12 good, <10 review THEORY.md + CODE_DEEP_DIVE.md.
