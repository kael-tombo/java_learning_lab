# Security Considerations for LRU Cache

1. **Cache poisoning**: Validate all cached data
2. **Sensitive data**: Don't cache passwords, tokens
3. **Memory exhaustion**: Enforce capacity limits
4. **Timing attacks**: LRU behavior may leak access patterns
5. **Thread safety**: Use ConcurrentHashMap or synchronization
6. **Resource cleanup**: Properly evict and close resources
