# Security — Distributed Locks

## Threats
- Lock hijacking (spoofing lock holder identity)
- Denial of service (exhaust lock resources)
- Replay attacks (re-use old fencing tokens)
- Unauthorized lock release

## Mitigations
- Authenticated lock clients (mTLS)
- Unique lock holder identifiers
- Token expiry and validation
- Audit logging of lock operations
- Rate limiting per client
