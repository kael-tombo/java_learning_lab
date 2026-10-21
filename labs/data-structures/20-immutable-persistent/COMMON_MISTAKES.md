# Common Mistakes

1. Mutable fields in supposedly immutable class
2. Exposing internal references (defeats immutability)
3. Not using @SuppressWarnings for generic array creation
4. Deep copy instead of structural sharing
5. Forgetting equals/hashCode for value objects
6. Memory leaks from retaining references to old versions
7. Stack overflow from deep recursion in long lists
