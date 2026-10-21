# How It Works — Distributed ID Generation

ID generation in distributed systems needs to produce unique, ordered identifiers without coordination between nodes.

Snowflake does this by combining timestamp + worker ID + sequence. Each worker gets a unique ID, and within the same millisecond, a counter ensures uniqueness. The result fits in a 64-bit long.

UUID v7 uses a similar approach but outputs 128 bits: timestamp plus random data. It follows the UUID standard for compatibility.

ULID is like a text-friendly UUID v7: same time + random structure but encoded in Base32 for human readability and sorting.

The key insight: by using timestamps as the first part of the ID, all schemes produce roughly time-ordered IDs that are database-index-friendly.
