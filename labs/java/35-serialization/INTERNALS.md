# Serialization — Internal Mechanics

## How Java Serialization Works Internally

### ObjectOutputStream Internals

When you call `ObjectOutputStream.writeObject(obj)`, the JVM:
1. Checks if the object implements `Serializable`
2. Looks up the class descriptor in its internal cache
3. Writes the class metadata (class name, serialVersionUID, field descriptors)
4. Writes the actual field values using reflection
5. Handles object references to maintain graph structure

### ObjectInputStream Internals

Deserialization reconstructs objects:
1. Reads class metadata from the stream
2. Locates the class definition (may trigger class loading)
3. Creates an uninitialized instance (bypasses constructor)
4. Populates fields from the stream data
5. Calls `readResolve()` if defined

### Serialization Graph

The serialization mechanism tracks object references to handle cyclic graphs. Each object is assigned a handle (integer ID). When an object is encountered again, only the handle is written, preserving the graph structure.

### serialVersionUID

This 64-bit hash is computed from the class structure. If the sender and receiver have different versions, `InvalidClassException` is thrown. Explicit declaration prevents this.

### Security Considerations

- Deserialization can execute arbitrary code via gadget chains
- Always validate or filter deserialized objects
- Use `ObjectInputFilter` (Java 9+) to restrict classes
- Avoid serializing sensitive data (use `transient`)
