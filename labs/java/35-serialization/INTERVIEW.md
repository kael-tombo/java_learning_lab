# Interview Questions: Serialization

## Company-Specific Focus

### Google
- Java serialization: ObjectOutputStream, ObjectInputStream, serialVersionUID
- Transient fields: skipping serialization for non-essential or derived data
- Custom writeObject/readObject for custom serialization logic
- Protocol Buffers: why Google created protobuf over Java serialization

### Microsoft
- Java serialization vs C# BinaryFormatter/DataContractSerializer
- Performance considerations: Java serialization is slow and insecure
- JSON with Jackson or Gson: modern serialization choices

### Amazon
- JSON serialization for REST APIs: Jackson, fasterxml, annotations
- Avro for Kafka: schema evolution for streaming data
- Kryo for high performance serialization within data pipelines

### Meta
- Serialization performance: Kryo vs Protobuf vs Avro vs JSON
- Serializable migration: adding serialVersionUID to existing classes
- Externalizable interface: complete control

### Apple
- Avoid Java serialization: security vulnerabilities, large payloads
- Using JSON for API responses and configuration
- Write replace/readResolve patterns for singleton control

### Oracle
- The Java serialization specification: Object Serialization Stream Protocol
- serialVersionUID: how it ensures class compatibility
- Secure serialization: deserialization filtering (JEP 290, 415)
- Java serialization deprecation plans

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| 297 Serialize and Deserialize Binary Tree | Hard | Google, Amazon, Apple, Microsoft | Tree serialization with delimiters |
| 271 Encode and Decode Strings | Medium | Amazon, Google, Apple | String list serialization with length prefix |
| 428 Serialize and Deserialize N-ary Tree | Hard | Amazon, Google | N-ary tree serialization |
| 449 Serialize and Deserialize BST | Medium | Amazon, Google, Apple | BST serialization using preorder |
| 535 Encode and Decode TinyURL | Medium | Google, Amazon, Apple | URL mapping serialization |

## Real Production Scenarios
- **Log4Shell**: Java deserialization of JNDI lookups caused a global security incident
- **Uber**: Java serialization of a large object graph caused OOM — migrated to Protocol Buffers
- **Netflix**: Deserialization filter (JEP 290) prevented a remote code execution attempt in production

## Interview Patterns & Tips
- **Always declare serialVersionUID**: to ensure class version compatibility during deserialization.
- **Transient**: fields that should not be serialized (passwords, derived data).
- **Externalizable**: When you need complete control over the serialized form.
- **ObjectInputStream filtering**: Always use a deserialization filter.
- **JSON, Protobuf, Avro**: Prefer these over Java serialization for modern systems.

## Deep Dive Questions
- **JVM**: How does Java serialization work at the JVM level? The ObjectOutputStream writes the class descriptor and field values to the stream.
- **Security**: What vulnerabilities exist in Java deserialization? How does the filter (JEP 290) mitigate them?
- **Performance**: What makes Java serialization slow compared to Kryo or Protobuf?
- **Memory**: How does serialization affect GC? Large object graphs create many temporary objects.
- **Compact strings in Java 9+**: How does compact string affect the serialized format of Strings?