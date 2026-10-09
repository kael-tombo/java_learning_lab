# Security — ID Generation

## ID Leakage
- Time-based IDs reveal creation time
- Sequential IDs reveal growth rate and volume
- Worker IDs in Snowflake reveal topology

## Mitigations
- Add random prefix/suffix for externally exposed IDs
- Use custom epoch to obscure absolute time
- Consider hash-based IDs for public exposure
- Rate limit ID generation to prevent enumeration

## UUID Security
- UUID v4 random bits should use SecureRandom
- Predictable random seeds enable ID guessing
- UUID v1 leaks MAC address and timestamp
