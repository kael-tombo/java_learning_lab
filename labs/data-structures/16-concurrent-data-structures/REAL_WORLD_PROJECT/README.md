# Real World Project: High-Frequency Trading Order Book

Build a concurrent order book for trading.
- Lock-free queues for order ingestion
- ConcurrentHashMap for order lookup
- AtomicLong for sequence numbers
- Fine-grained locking for price levels
