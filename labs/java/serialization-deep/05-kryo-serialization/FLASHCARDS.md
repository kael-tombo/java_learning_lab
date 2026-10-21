# Kryo Serialization -- Flashcards

## Spaced-Repetition Learning Cards

### Card 1
Q: What is serialization?
A: The process of converting an object's state into a byte stream for storage or transmission.

### Card 2
Q: What is deserialization?
A: The process of reconstructing an object from a byte stream.

### Card 3
Q: What interface enables serialization?
A: java.io.Serializable (marker interface).

### Card 4
Q: What is the transient keyword?
A: Marks a field as non-serializable. Its value is lost during serialization.

### Card 5
Q: What is serialVersionUID?
A: A version identifier for serializable classes, used for version compatibility.

### Card 6
Q: What does writeObject() do?
A: Custom method that controls how an object's data is written during serialization.

### Card 7
Q: What does readObject() do?
A: Custom method that controls how an object's data is read during deserialization.

### Card 8
Q: What is readResolve()?
A: Allows replacing the deserialized object, used for singletons and enums.

### Card 9
Q: What is writeReplace()?
A: Allows replacing the object being serialized with a different object (proxy pattern).

### Card 10
Q: How does Externalizable differ from Serializable?
A: Externalizable requires implementing writeExternal and readExternal for complete control.

### Card 11
Q: How does serialization handle circular references?
A: Using a handle table that assigns unique IDs to objects and references them by ID.

### Card 12
Q: Does deserialization use constructors?
A: No. It uses Unsafe.allocateInstance to create objects without constructors.

### Card 13
Q: What is a gadget chain?
A: A sequence of classes that when deserialized execute arbitrary code (security vulnerability).

### Card 14
Q: What is ObjectInputFilter?
A: A filter that controls which classes can be deserialized (JDK 9+).

### Card 15
Q: What is the magic number for Java serialization?
A: 0xACED (followed by version 0x0005).

### Card 16
Q: What happens when serialVersionUID doesn't match?
A: InvalidClassException is thrown during deserialization.

### Card 17
Q: Can static fields be serialized?
A: No. Static fields belong to the class, not the instance, and are not serialized.

### Card 18
Q: What is the Serialization Proxy pattern?
A: Using writeReplace to substitute a proxy during serialization and readResolve to restore the original.

### Card 19
Q: Which is faster: Kryo or Java serialization?
A: Kryo is 5-10x faster than Java serialization.

### Card 20
Q: Which uses Protobuf as its default serialization?
A: gRPC uses Protocol Buffers as its default serialization format.

### Card 21
Q: What does @JsonProperty do?
A: Jackson annotation that configures JSON property name and behavior.

### Card 22
Q: What is JAXB used for?
A: Java Architecture for XML Binding - marshalling Java objects to XML and back.

### Card 23
Q: How does Kryo achieve better performance?
A: Through class registration, avoiding metadata overhead, and using efficient buffer management.

### Card 24
Q: What is a varint in Protocol Buffers?
A: A variable-length integer encoding that uses fewer bytes for smaller values.
