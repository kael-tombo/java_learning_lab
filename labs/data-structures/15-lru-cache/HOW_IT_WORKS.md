# How LRU Cache Works

## Data Structure

`
HashMap: key → Node
Doubly Linked List: Head (MRU) →” ... →” Tail (LRU)
`

## Internal Operations

### Move to Head
`java
void moveToHead(Node node) {
    removeNode(node);   // disconnect from current position
    addToHead(node);    // add right after head sentinel
}
`

### Remove Node
`java
void removeNode(Node node) {
    node.prev.next = node.next;
    node.next.prev = node.prev;
}
`

### Add to Head
`java
void addToHead(Node node) {
    node.next = head.next;
    node.prev = head;
    head.next.prev = node;
    head.next = node;
}
`

### Evict LRU
`java
void evict() {
    Node tail = tail.prev;  // actual last node (before tail sentinel)
    removeNode(tail);
    map.remove(tail.key);
}
`
"@

System.Collections.Hashtable["INTERNALS.md"] = @"
# Internals of LRU Cache

## Node Structure

`java
class Node {
    int key;
    int value;
    Node prev;
    Node next;
}
`

## Sentinel Nodes

Using sentinel (dummy) head and tail nodes eliminates null checks:
`
head →” node1 →” node2 →” ... →” nodek →” tail
`

## Capacity Tracking

Cache size is tracked separately from map size (they should always match).

## Thread Safety

For concurrent access:
- Synchronize all methods
- Use ReadWriteLock for get vs put
- Use ConcurrentHashMap + atomic updates
