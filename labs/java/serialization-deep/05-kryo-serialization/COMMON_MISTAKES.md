# Kryo Serialization -- Common Mistakes

## Top 20 Common Mistakes

### 1. Missing serialVersionUID
Failing to declare serialVersionUID causes InvalidClassException when classes evolve. Always declare: private static final long serialVersionUID = 1L;

### 2. Deserializing Untrusted Data
Accepting serialized data from untrusted sources without filtering is the most common security vulnerability. Always use ObjectInputFilter.

### 3. Using Mutable Objects as Keys
If a mutable object is used as a HashMap key and mutated, the hash code changes, making the key unfindable after deserialization.

### 4. Ignoring Transient Fields
Fields marked transient lose their values during serialization. Ensure they are properly reinitialized after deserialization.

### 5. Asymmetric writeObject/readObject
The writeObject and readObject methods must be perfectly symmetrical. Writing two ints and reading one causes stream corruption.

### 6. Forgetting Default Methods
When overriding writeObject, you must call defaultWriteObject() unless you manually write all fields.

### 7. Inner Class Serialization
Non-static inner classes contain an implicit reference to the enclosing instance, causing unintended serialization of the outer class.

### 8. Circular References Without Tracking
Without reference tracking enabled, circular references cause StackOverflowError during serialization.

### 9. Constructor Bypass
Deserialization does not call constructors. Fields initialized in constructors must be restored in readObject.

### 10. Performance Ignorance
Using default serialization for latency-critical paths without considering performance implications.

### 11. ClassLoader Issues
Deserializing classes from different ClassLoaders causes ClassNotFoundException.

### 12. Enum Serialization
Enums are serialized by name only. Adding enum constants changes ordinal mapping on deserialization.

### 13. Large Object Graphs
Serializing massive object graphs without monitoring causes OOM and excessive latency.

### 14. Thread Safety
ObjectInputStream and ObjectOutputStream are not thread-safe. Concurrent access corrupts data.

### 15. Stream Leaks
Failing to close serialization streams in finally blocks causes resource leaks.

### 16. Version Compatibility
Not testing deserialization of old serialized data after class changes leads to production failures.

### 17. Proxy Bypass
Bypassing the serialization proxy by deserializing the main class directly defeats security measures.

### 18. Inconsistent Registration
Changing serializer registration order between serialization and deserialization corrupts data.

### 19. Slow Reflection
Default serialization uses reflection for every field. For performance-critical code, use custom serialization.

### 20. Schema Evolution Ignorance
Not planning for schema evolution when using Protobuf or similar frameworks leads to painful migrations.

## Prevention Strategies
1. Always declare serialVersionUID explicitly
2. Use ObjectInputFilter on all deserialization
3. Implement defensive copies in readObject
4. Test serialization compatibility with versioned data
5. Use static code analysis tools (SpotBugs, SonarQube)
6. Performance test with realistic data volumes
7. Document serialization format and versioning strategy
8. Review serialization code in code reviews
