# Performance — ID Generation

## Throughput (IDs/second)
| Generator | Single Thread | 8 Threads |
|-----------|--------------|-----------|
| Snowflake | 12M/s | 8M/s |
| UUID v7 | 8M/s | 6M/s |
| ULID | 5M/s | 4M/s |
| DB Seq | 50K/s | 50K/s |

## Bottlenecks
- Snowflake: System.currentTimeMillis() call (expensive on some OS)
- UUID v7: SecureRandom initialization
- ULID: Base32 encoding/decoding
- Sequence: Network round-trips for ranges

## Optimization
- Cache timestamp for single-millisecond batches
- Use ThreadLocalRandom instead of SecureRandom for non-security use
- Pre-encode ULID timestamp portion

## Memory
- Snowflake: ~24 bytes per instance
- UUID v7: ~32 bytes
- ULID: ~48 bytes (includes encoder state)
