# Quiz: LRU Cache

1. What data structure combination does LRU use? HashMap + Doubly Linked List
2. What is the time complexity of get? O(1)
3. Where is the MRU item in the list? At the head
4. Where is the LRU item? At the tail
5. What method in LinkedHashMap enables LRU? removeEldestEntry
6. What access order parameter enables LRU in LinkedHashMap? accessOrder=true
7. How does LFU differ from LRU? Evicts least frequent, not least recent
8. What are sentinel nodes? Dummy head/tail to avoid null checks
9. True/False: LRU is optimal for all access patterns. False
10. Which Redis eviction policy approximates LRU? allkeys-lru
