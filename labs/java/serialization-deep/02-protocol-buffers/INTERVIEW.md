# Interview Questions: Protocol Buffers

## Company-Specific Focus

### Google
- Protocol Buffers: language-neutral, platform-neutral serialization format
- .proto file: message definition language
- Code generation: protoc generates Java classes from .proto definitions

### Microsoft
- Protocol Buffers vs gRPC in Azure services
- Compatiblity: Proto3 is the standard version

### Amazon
- Protocol Buffers for microservice communication (gRPC)
- Schema evolution: backward and forward compatibility
- Performance: smaller, faster than JSON and XML

### Meta
- Required vs optional vs repeated fields in Proto2
- Oneof: union type in Protobuf
- Map type: key-value pairs in Protobuf

### Apple
- Proto3: simplified field rules (optional by default)
- Well-known types: Timestamp, Duration, Any, Struct
- JSON mapping: Protobuf can serialize to JSON

### Oracle
- Protocol Buffers: created at Google
- gRPC uses Protobuf as the interface definition language
- Java library: com.google.protobuf
- Builder pattern: generated immutable message classes

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| 297 Serialize and Deserialize Binary Tree | Hard | Google, Amazon, Apple | Protobuf-like tree serialization |
| 428 Serialize and Deserialize N-ary Tree | Hard | Amazon, Google | Schema-based serialization |

## Real Production Scenarios
- **Uber**: Migrating from Java serialization to Protobuf reduced message size by 60%
- **Netflix**: Protobuf for gRPC services improved inter-service communication performance

## Interview Patterns & Tips
- **Schema evolution**: Field numbers must never change; add new fields with new numbers
- **Backward compatibility**: new fields are optional; old clients see default values
- **Forward compatibility**: new fields are unknown to old clients; they are preserved
- **Performance**: binary format is smaller and faster than text formats

## Deep Dive Questions
- **Wire format**: How are Protobuf messages encoded on the wire? (Varint, zigzag)
- **Varint encoding**: How are integers encoded in Protobuf?
- **Field numbers**: What is the range of valid field numbers?
- **Reserved**: Why are reserved field numbers and names used?
- **gRPC integration**: How does Protobuf work as gRPC's IDL?