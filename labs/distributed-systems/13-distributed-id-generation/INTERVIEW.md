# Distributed ID Generation (Duplicate Lab) - Interview Preparation

> Key interview questions about globally unique ID generation in distributed systems.

---

## Core Interview Questions

### Q1: What properties should a distributed ID generator have?
**Answer**: Globally unique, monotonically increasing (for B-tree performance), compact (64-bit ideal), high throughput (millions/sec), available (no single point of failure), ordered (enable range queries by creation time).

### Q2: How does Instagram's ID generation work?
**Answer**: Uses PostgreSQL with logical sharding. Each shard has its own sequence. Shard ID encoded in ID: 41 bits for timestamp, 13 bits for shard ID, 10 bits for sequence. Pluggable into PostgreSQL's auto-increment. 4096 IDs/sec per shard.

### Q3: What is a "range-based" ID generation strategy?
**Answer**: Coordinator allocates ranges of IDs to workers. E.g., worker 1 gets [1-1000], worker 2 gets [1001-2000]. Workers generate IDs within range locally. When range depleted, request new range. Reduces coordinator load, but can skip IDs if worker restarts.

### Q4: How does Flake ID generation work?
**Answer**: Flake (Boundary's error-tolerant Snowflake variant). Uses worker ID, timestamp, and sequence. Allows timestamp to move backward slightly (within tolerance). Uses wall clock but tolerates minor NTP skew. Handles clock rollback by waiting.

### Q5: What's the difference between ordered and unordered IDs?
**Answer**: Ordered IDs (Snowflake, Flake): enable range scans by time, efficient B-tree insertion, human-readable time extraction. Unordered IDs (UUID v4): no ordering, random distribution across B-tree pages (cache miss), larger storage (128-bit). Ordered preferred for most OLTP databases.

## Company-Specific Focus

| Company | ID Generation Focus |
|---------|--------------------|
| Twitter | "Snowflake - de facto standard for distributed ID" |
| Instagram | "PostgreSQL-based sharded ID generation" |
| Google | "Spanner's commit timestamps as unique IDs" |
| Discord | "Flake - error-tolerant Snowflake variant" |

## LeetCode Connections

| Problem | # | ID Concept |
|---------|---|-----------|
| Encode and Decode TinyURL | 535 | ID to URL encoding |
| Unique Email Addresses | 929 | ID normalization |
| Design TinyURL | System Design | ID generation at scale |

## System Design Connections

- **Design a URL Shortener**: Base-62 encoding + Snowflake
- **Design a Photo Sharing App**: Snowflake for photos
- **Design a Messaging System**: Ordered message IDs
- **Design a Database**: Snowflake for primary keys

> **Key Insight**: Snowflake is the most common distributed ID question. Know the bit allocation and how to handle clock skew.