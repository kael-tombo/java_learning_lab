# JSON Serialization -- Exercises

## Beginner Exercises

### Exercise 1: Basic Operations
Implement a program that demonstrates core serialization and deserialization.
Write code to serialize an object to a file, deserialize it, and verify correctness.

### Exercise 2: Multiple Objects
Serialize a collection of objects and verify the round-trip preserves all data.
Test with Lists, Maps, and Sets containing custom objects.

### Exercise 3: Transient Fields
Experiment with transient fields and observe their behavior after deserialization.
Verify that transient fields return to their default values.

## Intermediate Exercises

### Exercise 4: Custom Serialization
Implement custom writeObject/readObject methods for fine-grained control.
Add validation logic in readObject to ensure data integrity.

### Exercise 5: Versioning
Simulate class evolution by adding/removing fields and testing compatibility.
Handle InvalidClassException and implement backward compatibility.

### Exercise 6: Externalizable
Implement the Externalizable interface for complete serialization control.
Compare performance with default serialization using JMH benchmarks.

## Advanced Exercises

### Exercise 7: Serialization Proxy
Implement the Serialization Proxy pattern to improve security and flexibility.
The proxy handles serialization while the main class focuses on business logic.

### Exercise 8: Security Filter
Configure ObjectInputFilter to whitelist allowed classes during deserialization.
Test that unauthorized classes are rejected.

### Exercise 9: Performance Benchmark
Write a JMH benchmark comparing different serialization approaches.
Measure throughput, latency percentiles, and output size for 100,000 objects.

### Exercise 10: Deep Object Graphs
Serialize deeply nested object graphs (10+ levels) and analyze:
- Memory usage during serialization
- Total serialization time
- Output stream size
- Impact of reference tracking on circular structures

## Challenge Exercise
Build a custom serialization framework from scratch that:
1. Writes objects without using Java serialization primitives
2. Supports schema evolution with version metadata
3. Achieves better performance than default Java serialization
4. Correctly handles circular references and shared objects
5. Includes a security filter to prevent deserialization attacks
