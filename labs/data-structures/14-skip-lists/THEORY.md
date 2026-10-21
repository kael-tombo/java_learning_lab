# Theory: Skip Lists

## Fundamentals

A skip list is a probabilistic data structure that allows O(log n) expected time for search, insert, and delete operations. It was invented by William Pugh in 1989. A skip list consists of multiple levels of linked lists, where each higher level is a "skip" over a subset of the elements in the level below.

## Structure

A skip list has:
- Multiple levels (typically log n levels)
- Each level is a sorted linked list
- Level 0 contains all elements
- Level i contains approximately n/2^i elements (on average)
- Each node has a random number of levels

## Level Distribution

Each node's level is determined by random level generation:
`
level = 1
while random() < 0.5 and level < MAX_LEVEL:
    level++
`

This gives a geometric distribution: P(level = k) = 1/2^k.

## Operations

### Search
`
search(key):
    current = header
    for level = MAX_LEVEL-1 down to 0:
        while current.forward[level].key < key:
            current = current.forward[level]
    current = current.forward[0]
    return current if current.key == key else null
`

### Insert
`
insert(key, value):
    update[] = array of MAX_LEVEL nodes
    current = header
    for level = MAX_LEVEL-1 down to 0:
        while current.forward[level].key < key:
            current = current.forward[level]
        update[level] = current
    current = current.forward[0]
    if current.key == key:
        current.value = value
    else:
        newLevel = randomLevel()
        newNode = createNode(key, value, newLevel)
        for level = 0 to newLevel:
            newNode.forward[level] = update[level].forward[level]
            update[level].forward[level] = newNode
`

### Delete
`
delete(key):
    update[] = array of MAX_LEVEL nodes
    current = header
    for level = MAX_LEVEL-1 down to 0:
        while current.forward[level].key < key:
            current = current.forward[level]
        update[level] = current
    current = current.forward[0]
    if current.key == key:
        for level = 0 to current.maxLevel:
            update[level].forward[level] = current.forward[level]
`

## Complexity

| Operation | Expected | Worst Case |
|-----------|----------|------------|
| Search | O(log n) | O(n) |
| Insert | O(log n) | O(n) |
| Delete | O(log n) | O(n) |
| Space | O(n) | O(n log n) |

The worst case occurs with very unlikely random level choices (all nodes at level 1).

## Comparison with Balanced Trees

| Property | Skip List | Red-Black Tree |
|----------|-----------|----------------|
| Implementation | Simple | Complex |
| Randomization | Yes | No (deterministic) |
| Expected height | O(log n) | O(log n) |
| Worst-case height | O(n) | O(log n) |
| Concurrency | Easy | Hard |
| Range queries | Good | Good |
