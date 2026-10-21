# Theory of Distributed ID Generation

## 1. The Problem of Distributed IDs

In a single-node system, auto-incrementing database sequences provide unique, ordered IDs. In distributed systems, multiple nodes generate IDs concurrently, creating challenges:

- **Uniqueness**: No two nodes must generate the same ID
- **Ordering**: IDs should reflect creation order when possible
- **Scalability**: ID generation must not become a bottleneck
- **Availability**: Nodes should generate IDs without coordination

## 2. ID Generation Strategies

### 2.1 Centralized Coordination
- A single service issues ID ranges to nodes
- Example: Database sequence, ZooKeeper sequential znode
- Pros: Simple, guaranteed uniqueness and ordering
- Cons: Single point of failure, scalability bottleneck

### 2.2 Time-Based + Node ID
- IDs combine timestamp with a unique node identifier
- Example: Snowflake, Flake, ShardID
- Pros: No coordination needed after initial node ID assignment
- Cons: Clock skew can cause issues; node ID management

### 2.3 Random IDs
- High-entropy random or UUID-based IDs
- Example: UUID v4, random 128-bit values
- Pros: No coordination whatsoever
- Cons: No ordering, larger storage, collision probability

### 2.4 Hybrid Approaches
- Combine time, node ID, and sequence number
- Example: Snowflake, ULID, UUID v7
- Best of all worlds: ordered, unique, scalable

## 3. The Snowflake Algorithm

Twitter's Snowflake generates 64-bit IDs:
- 1 bit: reserved (sign bit, always 0)
- 41 bits: timestamp in millisecond (69 years)
- 10 bits: worker/node ID (1024 nodes)
- 12 bits: sequence number (4096 IDs/ms/node)

### Properties
- 64-bit integer, fits in long
- Time-ordered (monotonic within same node)
- Up to 4 million IDs/second per datacenter
- Decentralized generation

## 4. UUID Standards

### UUID v4 (Random)
- 122 random bits + 6 version/variant bits
- No ordering, unpredictable
- Collision probability: extremely low

### UUID v6 (Time-Ordered)
- Based on v1 but with timestamp first
- DB-friendly ordering
- Requires MAC address or random node ID

### UUID v7 (Timestamp + Random)
- 48-bit Unix timestamp (ms)
- 74 random bits
- Ordered by time, fits in UUID standard

## 5. ULID

ULID is a 128-bit identifier with:
- 48-bit timestamp (millisecond, Unix epoch)
- 80-bit random component
- 26-character Crockford Base32 encoding
- Case-insensitive, sortable

### Properties
- 1.21e+24 unique ULIDs per millisecond
- Lexicographically sortable
- URL-safe (no special characters)
- Monotonic within same millisecond

## 6. Performance and Storage

| Scheme | Bit Size | Storage | Ordering | Collision Risk |
|--------|----------|---------|----------|----------------|
| Snowflake | 64 | 8 bytes | Time (per node) | None (per node) |
| UUID v4 | 128 | 16 bytes | None | Extremely low |
| UUID v7 | 128 | 16 bytes | Time | Extremely low |
| ULID | 128 | 16 bytes | Time | Extremely low |
| DB Sequence | 32-64 | 4-8 bytes | Perfect | None |

## 7. Collision Probability

For random 128-bit IDs:
- After 1 billion IDs: collision probability ~ 2.7e-19
- After 2^64 IDs: ~50% collision probability

For Snowflake:
- Zero collisions within same worker + timestamp + sequence space
- Collisions only possible with clock rollback or misconfigured workers
