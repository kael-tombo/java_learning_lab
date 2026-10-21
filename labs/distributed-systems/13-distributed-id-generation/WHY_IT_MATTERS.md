# Why Distributed ID Generation Matters

Distributed ID generation is foundational:
- Every distributed system needs unique identifiers
- IDs must be generated without coordination
- Ordering helps with indexing and debugging
- Format matters for storage efficiency (64-bit vs 128-bit)
- Choosing wrong scheme leads to performance issues

Without proper distributed ID generation, systems face:
- Primary key conflicts on merge
- Poor database index performance
- Unnecessary coordination overhead
- Hard-to-debug data issues
