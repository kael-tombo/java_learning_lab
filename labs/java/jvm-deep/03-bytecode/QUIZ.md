# QUIZ — Bytecode Serialization

## 1. What is the byte layout of a serialized node?
<details>
<summary>Answer</summary>
[4 bytes: value][4 bytes: child count][children...]. Each field is 4 bytes (32-bit signed integer, big-endian).
</details>

## 2. What traversal order does the serialization use?
<details>
<summary>Answer</summary>
Pre-order (node first, then children recursively). This enables single-pass deserialization.
</details>

## 3. What does DataOutputStream.writeInt() write?
<details>
<summary>Answer</summary>
4 bytes in big-endian order (most significant byte first). Range: -2³¹ to 2³¹-1.
</details>

## 4. What happens if you deserialize a corrupted stream?
<details>
<summary>Answer</summary>
DataInputStream throws IOException (EOFException if stream ends early, or corrupted data may produce garbage values without error until later).
</details>

## 5. What's the space complexity of serializing an N-node tree?
<details>
<summary>Answer</summary>
O(N) bytes. Each node uses 8 bytes (4 for value + 4 for child count) plus children data.
</details>

## 6. Why use pre-order traversal?
<details>
<summary>Answer</summary>
Single-pass deserialization: read node, then recursively read its children in order. Post-order would require storing children before parent.
</details>

## 7. How do you handle trees deeper than the call stack?
<details>
<summary>Answer</summary>
Use iterative deserialization with explicit stack, or increase JVM stack size (-Xss). Recursive approach hits StackOverflowError at ~10k depth.
</details>

## 7. What's the space overhead vs JSON?
<details>
<summary>Answer</summary>
Binary: ~8 bytes/node. JSON: ~20-50 bytes/node (braces, quotes, commas, whitespace). Binary is 2-6x smaller.
</details>

## 8. How to handle integers > 2³¹-1?
<details>
<summary>Answer</summary>
Use writeLong/readLong (8 bytes), or variable-length encoding (LEB128) for arbitrary size.
</details>

## 9. What happens if stream ends mid-node?
<details>
<summary>Answer</summary>
DataInputStream throws EOFException. Always validate stream length or use length prefix.
</details>

## 10. How to extend format for string values?
<details>
<summary>Answer</summary>
Write string length (int/varint) + UTF-8 bytes. For variable length, use LEB128 length prefix.
</details>