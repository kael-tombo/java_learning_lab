# Visual Guide — Distributed ID Generation

## Snowflake Bit Layout
`
 0                   41                  51           63
├────────────────────┼───────────────────┼────────────┤
│    Timestamp       │   Worker ID       │   Sequence │
│    (41 bits)       │    (10 bits)      │  (12 bits) │
├────────────────────┼───────────────────┼────────────┤
`

## UUID v7 Layout
`
 0                   48            52         64
├────────────────────┼──────────────┼─────────┤
│    Timestamp       │   Version    │  Random  │
│    (48 bits)       │   (4 bits)   │ (12 bits)│
├────────────────────┼──────────────┼─────────┤
64                                       128
├────────────────────────────────────────┤
│              Random (64 bits)           │
├────────────────────────────────────────┤
`
"@ }
          "INTERNALS.md" { @"
# Internals — Distributed ID Generation

## Snowflake State
- lastTimestamp: long (last used timestamp)
- sequence: int (current sequence in ms)
- workerId: int (configured at startup)

## UUID v7 Bits
- 48-bit timestamp (Unix ms)
- 4-bit version (0111 = v7)
- 12-bit random + 2-bit variant
- 62 more random bits

## ULID Encoding
- Crockford Base32: 0-9, A-Z (excluding I, L, O, U)
- 26 characters for 128 bits
- First 10: timestamp (48 bits)
- Last 16: random (80 bits)
