# Theory: Immutable & Persistent Data Structures

## Fundamentals

Immutable data structures cannot be modified after creation. Persistent data structures preserve previous versions when modified. They use structural sharing to make operations efficient: new versions share most of their structure with old versions.

## Immutability Benefits

- Thread safety: No synchronization needed
- Reasoning: No unexpected state changes
- Caching: Values never become stale
- Failure atomicity: Operations either complete or don't
- Equality: Two instances with same state are interchangeable

## Persistence Types

- **Ephemeral**: Modifications destroy previous version
- **Persistent**: Modifications preserve previous version
- **Partially persistent**: Can query old versions, only modify latest
- **Fully persistent**: Can modify old versions (creates branches)

## Structural Sharing

The key to efficiency: when creating a new version, only the nodes along the path from root to the modified leaf are copied. All other nodes are shared with the previous version.

## Complexity

| Operation | Ephemeral | Persistent |
|-----------|-----------|------------|
| List add | O(1) | O(1) |
| List get | O(1) | O(n) |
| BST insert | O(log n) | O(log n) |
| BST search | O(log n) | O(log n) |
| Map put | O(log n) | O(log n) |

Persistent operations have the same asymptotic complexity as their ephemeral counterparts because structural sharing limits copying to O(log n) nodes.
