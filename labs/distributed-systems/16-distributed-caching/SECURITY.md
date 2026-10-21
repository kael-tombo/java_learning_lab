# Security — Distributed Caching

## Threats
- Cache poisoning (malicious data injection)
- Data leakage from cache (sensitive data exposure)
- Cache flooding (DoS via cache-miss requests)

## Mitigations
- Encryption of cached sensitive data
- Authentication and ACLs for cache servers
- Input validation before caching
- Rate limiting per key pattern
- Proper key namespace isolation
