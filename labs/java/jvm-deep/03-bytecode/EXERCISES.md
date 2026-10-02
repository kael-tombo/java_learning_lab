# EXERCISES — Bytecode Serialization

## 1. Extend the Format (Beginner)

Add support for **string values** in tree nodes:

1. Modify the Node class to store `String value` instead of `int`
2. Update serialization: write string length (int) + UTF-8 bytes
2. Update deserialization to read string length + UTF-8 bytes
3. Test with tree containing: "root" → ["left", "right"]

**Challenge**: Handle empty strings and strings > 65535 chars.

---

## 2. Variable-Length Encoding (Intermediate)

Replace fixed 4-byte integers with **LEB128** (Little Endian Base 128) encoding:

```java
// Write unsigned int as LEB128
void writeVarInt(DataOutputStream out, int value) {
    while ((value & ~0x7F) != 0) {
        out.writeByte((value & 0x7F) | 0x80);
        value >>>= 7;
    }
    out.writeByte(value & 0x7F);
}
```

Tasks:
1. Implement `writeVarInt` / `readVarInt`
2. Modify serialization to use variable-length encoding
3. Measure space savings on a tree with values 0-1000

---

## 3. Iterative Deserialization (Advanced)

Replace recursive deserialization with **explicit stack** to avoid StackOverflowError on deep trees:

```java
Node deserializeIterative(DataInputStream dis) {
    // Use explicit stack: each entry = (parent, remainingChildren)
    // Process nodes in pre-order without recursion
}
```

**Challenge**: Handle trees with depth > 10,000 without StackOverflowError.

---

## 4. Type Polymorphism (Advanced)

Extend format to support **heterogeneous node types**:

```
[1 byte: type][payload...]
Types: 0=IntNode, 1=StringNode, 2=DoubleNode, 3=CustomNode
```

Tasks:
1. Design type registry (type byte → factory function)
2. Implement serialize/deserialize with type dispatch
3. Add type registry serialization for round-trip

---

## 5. Memory-Mapped Serialization (Advanced)

Use `FileChannel.map()` for zero-copy serialization of huge trees:

```java
// Write directly to memory-mapped file
MappedByteBuffer map = channel.map(FileChannel.MapMode.READ_WRITE, 0, size);
// Write directly to buffer
```

Tasks:
1. Implement `serializeToMappedFile(Node root, FileChannel channel)`
2. Implement `deserializeFromMappedFile(FileChannel)`
3. Benchmark vs ByteArrayOutputStream for 10M nodes

---

## 6. Delta Encoding (Challenge)

For trees with similar values, implement **delta encoding**:

```
[baseValue][delta1][delta2][delta2]...
```

Where each value is stored as difference from parent. Tasks:
1. Implement delta serialization/deserialization
2. Analyze space savings on a tree with small incremental changes
3. Handle negative deltas (zigzag encoding)

---

## 6. Concurrent Serialization (Challenge)

Parallelize serialization of independent subtrees:

```java
byte[] serializeParallel(Node root, int threadCount) {
    // Partition children among threads
    // Each thread serializes subtree to byte array
    // Combine results in order
}
```

**Challenge**: Maintain pre-order traversal order while parallelizing.