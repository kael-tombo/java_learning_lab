# Interview Questions: Java Serialization

## Company-Specific Focus

### Google
- Java serialization: ObjectOutputStream/ObjectInputStream
- serialVersionUID: version control for serialized classes
- Custom serialization: writeObject, readObject, readResolve, writeReplace

### Microsoft
- Java serialization vs .NET BinaryFormatter
- Transient fields: excluding sensitive or derived data

### Amazon
- Security: Java deserialization vulnerabilities (Log4Shell, etc.)
- JEP 290: deserialization filtering for security
- Migrating away: JSON, Protobuf, Avro as modern alternatives

### Meta
- Performance: Java serialization is slow and produces large output
- readObject vs readResolve: controlling deserialization behavior
- Externalizable: complete control over serialization format

### Apple
- Serialization proxy: using writeReplace for evolution-friendly serialization
- Enum serialization: special handling by the JVM

### Oracle
- Java Object Serialization Specification
- Serialization mechanism: writing class descriptor and field values
- serialVersionUID: computed from class structure
- Security: deserialization vulnerabilities

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| 297 Serialize and Deserialize Binary Tree | Hard | Google, Amazon, Apple | Tree serialization with custom format |
| 271 Encode and Decode Strings | Medium | Amazon, Google, Apple | String list serialization |
| 428 Serialize and Deserialize N-ary Tree | Hard | Amazon, Google | N-ary tree serialization |
| 449 Serialize and Deserialize BST | Medium | Amazon, Google, Apple | BST serialization with preorder |
| 535 Encode and Decode TinyURL | Medium | Google, Amazon, Apple | URL mapping serialization |

## Real Production Scenarios
- **Log4Shell (CVE-2021-44228)**: Remote code execution via JNDI deserialization in Log4j
- **Netflix**: Deserialization filter (JEP 290) prevented RCE in legacy services

## Interview Patterns & Tips
- **Always specify serialVersionUID**: ensures compatible deserialization
- **Transient**: mark sensitive fields as transient
- **Externalizable**: for complete control over serialization
- **Use alternatives**: prefer JSON, Protocol Buffers, or Avro

## Deep Dive Questions
- **Write protocol**: How does ObjectOutputStream write an object?
- **Object graph**: How does serialization handle cyclic object graphs?
- **serialVersionUID**: How is it computed from class structure?
- **readResolve**: How does readResolve replace the deserialized object?
- **Security**: What makes Java deserialization vulnerable to RCE attacks?