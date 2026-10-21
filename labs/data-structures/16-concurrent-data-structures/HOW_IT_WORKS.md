# How Concurrent Data Structures Work

## Treiber Stack (Lock-Free Stack)

Uses CAS on the top pointer:
`
push(x):
    do:
        oldTop = top
        newTop.next = oldTop
    while !CAS(&top, oldTop, newTop)

pop():
    do:
        oldTop = top
        if oldTop == null: return null
        newTop = oldTop.next
    while !CAS(&top, oldTop, newTop)
    return oldTop.value
`

## Michael-Scott Queue (Lock-Free Queue)

Uses CAS on head and tail pointers with a sentinel node. The tail can lag behind the actual end, requiring help from other threads to advance it.

## ConcurrentHashMap

Uses lock striping: the hash table is divided into segments (or bins), each with its own lock. Multiple threads can modify different segments concurrently.

## AtomicInteger

Uses CAS internally:
`
incrementAndGet():
    do:
        old = value
        new = old + 1
    while !CAS(&value, old, new)
    return new
`
"@

System.Collections.Hashtable["INTERNALS.md"] = @"
# Internals of Concurrent Data Structures

## Memory Ordering

Modern processors reorder instructions for performance. Memory barriers prevent reordering:
- Volatile: prevents reordering, ensures visibility
- CAS: full memory barrier (acquire + release)
- LazySet: store barrier only

## The ABA Problem

When a pointer changes from A to B and back to A between reads, CAS succeeds incorrectly. Solution: use AtomicStampedReference (combines pointer + version counter).

## Cache Coherence

- MESI protocol: Modified, Exclusive, Shared, Invalid
- False sharing: threads modify adjacent data, causing cache line bouncing
- Padding: align data to avoid false sharing

## Lock Striping in ConcurrentHashMap

Before Java 8: separate locks per segment. Java 8+: CAS for individual bins, synchronized for bin expansion.
