# Kryo Serialization — Mathematical Foundation

## 1. Variable-Length Integer Encoding

### Kryo Varint Format
Kryo uses a variable-length integer format similar to protobuf:
- 1-5 bytes for 32-bit integers
- 1-9 bytes for 64-bit integers
- Lower values encode in fewer bytes

### Encoding Scheme
Kryo's varint uses 7 data bits per byte:
- bytes(n) = ceil(log2(n+1) / 7) for n >= 0
- Negative numbers: write as (n << 1) for efficiency
- Optimization: small ints (-64 to 63) encode in 1 byte

## 2. Reference Tracking Mathematics

### Reference ID Encoding
When reference tracking is enabled:
- First occurrence: full object serialization
- Subsequent references: variable-length reference ID (1-5 bytes)
- Reference IDs are sequential (0, 1, 2, ...)
- Most recent 32 references use 1-byte IDs (-32 to -1 offset)

### Break-Even Point
Reference tracking is beneficial when:
objectCount > 2 and shared references > 1
The overhead of tracking is O(1) per object, worth it for any object with multiple references.

## 3. Serializer Registration

### Registration ID Mapping
Registered classes get sequential IDs:
- Registration ID i maps to class C_i
- Both sides must maintain identical registration order
- First 8 registered classes use 1-byte ID
- Next 512 classes use 2-byte IDs

### Performance Impact of Registration Order
- Frequently serialized classes: register first (small IDs)
- Classes with IDs 0-7: 1 byte overhead
- Classes with IDs 8-519: 2 bytes overhead
- Classes with IDs 520+: 3-5 bytes overhead

## 4. Output Buffer Mathematics

### Buffer Growth Strategy
Kryo's Output buffer grows by doubling:
- Initial size: default 4096 bytes (configurable)
- Growth: min(max(initialSize, required), maxBufferSize)
- Reallocation cost: O(bufferSize) for array copy

### Optimal Buffer Sizing
For serialization of N objects of average size S:
- Optimal initial buffer = expectedOutputSize * 1.2 (20% headroom)
- ExpectedOutputSize = N * averageObjectSerializedSize

## 5. Thread-Safe Pooling

### Pool Utilization
KryoPool maintains a queue of Kryo instances:
- borrow(): O(1) from queue head
- release(): O(1) to queue tail
- Pool size limits {min, max} instances

### Contention Probability
With T threads and P pool size:
- If P >= T: zero contention (each thread gets exclusive instance)
- If P < T: contention probability = (T-P)/T for each borrow

## Summary
Kryo's mathematical foundation focuses on compact integer encoding and registration-based class identification, enabling its superior performance characteristics.
