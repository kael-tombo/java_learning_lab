# Why Distributed ID Generation Exists

Auto-increment IDs don't work in distributed systems: every node would need to coordinate to get the next value, creating a bottleneck.

The solution is to generate IDs locally using information available to each node: the current time and a unique node identifier. This eliminates the need for coordination while guaranteeing uniqueness.

Each scheme (Snowflake, UUID v7, ULID) makes different trade-offs:
- Snowflake: compact (64-bit), requires worker configuration
- UUID v7: standard-compliant, self-configuring
- ULID: human-readable, URL-safe, sortable
