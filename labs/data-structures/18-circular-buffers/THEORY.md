# Theory: Circular Buffers & Ring Buffers

## Fundamentals

A circular buffer is a fixed-size data structure that uses a single, contiguous block of memory as if it were circular. Data is written at the tail pointer and read from the head pointer. When a pointer reaches the end of the buffer, it wraps around to the beginning.

## Structure

- Fixed-size array of N elements
- Head pointer: points to next element to read
- Tail pointer: points to next free slot to write
- Size: number of elements currently stored

## Operations

- offer/add: write element at tail, advance tail
- poll: read element from head, advance head
- peek: read element from head without removing
- isFull, isEmpty: check state

## Policies

### Overwrite Policy
When full, new writes overwrite oldest elements (advance head).

### Blocking Policy
When full, writers block until space is available.
