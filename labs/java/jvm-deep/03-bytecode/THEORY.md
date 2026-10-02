# THEORY — Bytecode Serialization & Deserialization

## Overview

This lab explores **byte-level serialization and deserialization** of tree structures — a fundamental technique for efficient storage and transmission of hierarchical data. Unlike text-based formats (JSON, XML), binary serialization produces compact, fast-to-parse representations that mirror the data's natural memory layout.

## Core Concepts

### 1. Binary Serialization

Binary serialization writes data directly as bytes rather than text. For an N-ary tree:

```
Node format: [4 bytes: value][4 bytes: child count][children...]
```

Each node:
- **4 bytes**: Integer value (32-bit signed)
- **4 bytes**: Child count (32-bit signed)
- **Children**: Recursively serialized in pre-order

### 2. Stream-Based I/O

Java's `DataOutputStream` / `DataInputStream` provide platform-independent binary I/O:

```java
// Writing
DataOutputStream dos = new DataOutputStream(byteArrayOutputStream);
dos.writeInt(value);
dos.writeInt(childCount);

// Reading
DataInputStream dis = new DataInputStream(inputStream);
int value = dis.readInt();
int childCount = dis.readInt();
```

### 3. Tree Traversal Order

**Pre-order traversal** (node before children) enables single-pass deserialization:
- Serialize: Write node → recurse children
- Deserialize: Read node → recurse children

---

## Key Algorithms

### Serialization Algorithm
```
serialize(node):
  if node is null: return empty bytes
  write node.value (4 bytes)
  write node.children.size() (4 bytes)
  for each child:
      serialize(child)
```

### Deserialization Algorithm
```
deserialize(stream):
  if stream exhausted: return null
  value = readInt()
  childCount = readInt()
  node = new Node(value)
  repeat childCount times:
      child = deserialize()
      node.children.add(child)
  return node
```

## Complexity Analysis

| Operation   | Time   | Space   |
|-------------|--------|---------|
| Serialize   | O(N)   | O(N)    |
| Deserialize | O(N)   | O(N)    |

**Storage**: 8 bytes per node (4 for value + 4 for child count) + recursive children data.

---

## Key Insights

1. **Byte-level encoding**: Using `DataOutputStream`/`DataInputStream` for compact binary serialization
2. **Recursive structure**: The recursive nature mirrors the tree's structure — deserialization is a pre-order walk
3. **No metadata overhead**: Unlike JSON/XML, binary encoding has minimal framing overhead
4. **Extensibility**: Format can be extended with type markers, strings, or variable-length encoding (e.g., for large trees or text values)

---

## Common Pitfalls

| Pitfall | Prevention |
|---------|------------|
| Endianness mismatch | Use `DataOutputStream`/`DataInputStream` (big-endian by default) |
| Integer overflow | Use `long` if values exceed 2³¹-1 |
| Empty tree handling | Special case: return empty byte array for null |
| Stream corruption | Always check stream bounds; use `try-with-resources` |
| Large trees | Consider iterative approach to avoid stack overflow |

---

## Extensions & Variations

| Variation | Use Case |
|-----------|----------|
| Variable-length encoding (LEB128) | Large trees with small values |
| String values | Prefix with length + UTF-8 bytes |
| Type markers | Heterogeneous node types |
| Compression (gzip/zstd) | Large trees, network transmission |
| Memory-mapped files | Large trees, random access |