# Java Serialization — Mathematical Foundation

## 1. Asymptotic Complexity Analysis

### Big-O Notation for Serialization Operations
- **Object graph traversal**: O(n) where n is number of objects
- **Field serialization**: O(f) where f is total fields across all objects
- **Handle table operations**: O(1) per object (amortized)
- **Stream parsing**: O(s) where s is stream size in bytes

### Memory Complexity
- **Serialization buffer**: O(output size) proportional to object graph
- **Handle table**: O(object count) for reference tracking
- **Class descriptor cache**: O(class count) for type metadata

### Amortized Analysis
The cost of serializing a deeply nested object graph is amortized O(1) per node when using iterative traversal with a stack.

## 2. Stream Format Mathematics

### Header and Magic Number
Java serialization stream begins with:
- Magic number: 0xACED (2 bytes)
- Stream version: 0x0005 (2 bytes)
- Total header: 4 bytes

### Class Descriptor Encoding
Each class descriptor includes:
- Class name length (2 bytes) + name bytes (n bytes)
- serialVersionUID (8 bytes)
- Field count (2 bytes)
- Per field: type code (1 byte) + name length (2 bytes) + name bytes

### Handle Assignment
Handles are zero-indexed integers assigned sequentially:
- Base handle for first object: 0x007E0001
- Each subsequent object receives handle + 1
- Handles are written as 4-byte integers with base offset

## 3. serialVersionUID Mathematics

### Hash Computation
The default serialVersionUID is computed as a SHA-1 hash of the class structure:
1. Class name, modifiers, interfaces are hashed
2. Field names, types, modifiers are hashed
3. Method names, return types, parameters are hashed
4. Result is truncated to 64 bits

### Probability of Collision
With 64-bit hash space:
- Birthday paradox: ~50% probability of collision after 2^32 classes
- For practical purposes (~10^4 classes): negligible

## 4. Size Estimation

### Object Graph Size Formula
TotalStreamSize = Header(4) + Σ(ClassDescriptors) + Σ(ObjectData) + HandleTable + Footer

### Example Calculation
For a simple Point class (int x, int y):
- Header: 4 bytes
- Class descriptor: ~30 bytes
- Two int fields: 8 bytes
- Object reference: 4 bytes (handle)
- Total: ~46 bytes per object

## 5. Probability in Deserialization

### Malformed Stream Detection
The probability of random bytes forming a valid serialization stream is approximately:
- P(magic + version match) = 1/2^32 (for random 4-byte prefix)
- Additional structural validation reduces this further

## Mathematical Formulas

### Stream Growth Rate
For an object graph with N objects and F total fields:
- Best case (all primitives): ~30 + 4*N + 4*F bytes
- Average case: ~100 + 50*N + 8*F bytes
- Worst case (long strings, many classes): unbounded

### Handle Table Size
handleTableSize = baseOffset + objectCount * handleEntrySize
- baseOffset = 0x007E0000
- handleEntrySize = 4 bytes (int)

## Summary
Understanding the mathematics behind Java serialization stream format enables accurate size estimation, performance prediction, and debugging of serialization issues.
