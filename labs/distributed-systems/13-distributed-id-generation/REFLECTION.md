# Reflection — Distributed ID Generation

## Key Questions
1. When would you choose Snowflake over UUID v7?
2. How does ID scheme affect database performance?
3. What happens when the timestamp wraps around?
4. How do you migrate between ID schemes?

## Review Points
- Understand bit allocation trade-offs
- Consider peak throughput requirements
- Plan for worker ID management
- Test with concurrent access patterns

## Connections
- Database indexing and sharding
- Distributed systems time ordering
- Data serialization formats
