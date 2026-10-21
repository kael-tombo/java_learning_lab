# Step-by-Step: Building a Circular Buffer

1. Allocate fixed-size Object array
2. Initialize head=0, tail=0, size=0
3. Implement offer: if not full, write at tail, advance tail
4. Implement add: always write at tail, advance tail and head if full
5. Implement poll: if not empty, read from head, advance head
6. Implement peek: read from head without advancing
7. Test wrap-around behavior
8. Add blocking operations with conditions
9. Test thread safety
