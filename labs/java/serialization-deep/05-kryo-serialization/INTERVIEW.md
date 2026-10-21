# Interview Questions: Kryo Serialization

## Company-Specific Focus

### Google
- Kryo: fast, efficient Java serialization framework
- Registration: registering classes for optimized serialization
- Serializer: custom serializer implementations

### Microsoft
- Kryo vs messagepack/protobuf
- Pooling: Kryo instance pooling for thread safety

### Amazon
- Performance: Kryo is 10x faster than Java serialization with smaller output
- Spark/Kafka: Kryo is the default serialization in Apache Spark
- Registration strategy: factory for thread-safe Kryo instances

### Meta
- Kryo configuration: registration required, unregistered types are slower
- Thread safety: Kryo instances are not thread safe — use ThreadLocal or pooling
- FieldSerializer: default serializer, uses reflection

### Apple
- Kryo vs Protobuf: binary format comparision
- Zero-config: Kryo can work without registration

### Oracle
- Kryo is a third-party library (not in JDK)
- Used in distributed systems (Spark, HBase, Cassandra)
- Compact format: Kryo writes field types only once per class

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| (No direct LC problems — Kryo is a serialization framework used in data systems) |

## Real Production Scenarios
- **Uber**: Spark jobs using Kryo serialization improved performance by 5x over Java serialization
- **Amazon**: Kryo for inter-service caching — smaller payloads reduced Redis memory usage by 50%

## Interview Patterns & Tips
- **Performance**: significantly faster than Java serialization
- **Registration**: register classes for optimal serialization
- **Thread safety**: Kryo instances are not thread safe
- **Pooling**: use KryoPool or ThreadLocal for concurrent access

## Deep Dive Questions
- **Kryo vs Java serialization**: Why is Kryo faster?
- **Registration**: What does class registration do?
- **Serializer types**: What serializers does Kryo provide?
- **Thread safety**: How to manage Kryo instances in multithreaded environments?
- **Spark integration**: How is Kryo used in Apache Spark?