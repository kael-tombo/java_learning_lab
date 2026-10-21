# Flashcards: LRU Cache

## Front: What is an LRU cache?
Back: A bounded cache that evicts the least recently used item when full.

## Front: How does LRU achieve O(1) operations?
Back: HashMap for key lookup, doubly linked list for order maintenance.

## Front: What is the eviction policy?
Back: When at capacity, remove the item at the tail (least recently used).

## Front: How does get() affect order?
Back: The accessed item is moved to the head (most recently used).

## Front: What is LFU vs LRU?
Back: LFU tracks access frequency, LRU tracks recency.
