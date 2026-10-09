# Architecture — ID Generation

## Component Diagram
`
ID Generation Service
    |
    +-- SnowflakeGenerator
    |     - Timestamp source (System.currentTimeMillis)
    |     - Worker ID allocation
    |     - Sequence counter
    |
    +-- UuidV7Generator
    |     - Timestamp source
    |     - SecureRandom for randomness
    |
    +-- UlidGenerator
    |     - Timestamp source
    |     - Crockford Base32 encoder
    |
    +-- Registry
          - Worker ID assignment
          - Heartbeat monitoring
`

## Deployment Considerations
- Snowflake: needs worker ID config or registry
- UUID v7: fully decentralized, no config needed
- ULID: fully decentralized
- Sequence: requires coordination (DB, ZK, etc.)
