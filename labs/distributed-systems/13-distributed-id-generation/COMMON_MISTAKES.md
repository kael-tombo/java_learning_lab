# Common Mistakes — Distributed ID Generation

1. Ignoring clock rollback (assumes monotonic clock)
2. Insufficient sequence bits for peak throughput
3. Static worker ID assignment without validation
4. Not handling system clock adjustments
5. Using weak random for UUID v4
6. Base32 encoding errors in ULID
7. Not testing concurrent generation
