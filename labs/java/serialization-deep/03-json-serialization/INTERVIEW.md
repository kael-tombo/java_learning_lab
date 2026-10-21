# Interview Questions: JSON Serialization

## Company-Specific Focus

### Google
- Jackson: most popular JSON library in Java ecosystem
- Gson: Google's JSON library, simpler but less feature-rich
- ObjectMapper: Jackson's core class for reading/writing JSON

### Microsoft
- Jackson vs System.Text.Json (.NET)
- JSON-B: Java standard for JSON binding

### Amazon
- JSON for REST APIs: most common format for service-to-service communication
- Jackson streaming API: JsonParser, JsonGenerator for large payloads
- JSON Schema validation for API contracts

### Meta
- Jackson annotations: @JsonProperty, @JsonIgnore, @JsonFormat, @JsonCreator
- Polymorphic serialization: @JsonTypeInfo for inheritance hierarchies
- Custom serializers: JsonSerializer, JsonDeserializer for custom types

### Apple
- Immutable objects: Jackson with constructor-based creators
- Records: Jackson supports Java 14+ records out of the box

### Oracle
- JSON-B (JSR 367): standard Java API for JSON binding
- Jackson: the de facto standard library
- Yasson: reference implementation of JSON-B
- Performance: streaming API vs object mapping

## LeetCode-Related Questions
| LC Problem | Difficulty | Companies | Notes |
|------------|------------|-----------|-------|
| 297 Serialize and Deserialize Binary Tree | Hard | Google, Amazon, Apple | JSON-like tree serialization |
| 271 Encode and Decode Strings | Medium | Amazon, Apple, Google | JSON-like string encoding |

## Real Production Scenarios
- **Netflix**: Jackson deserialization of large JSON caused OOM — migrated to streaming API
- **LinkedIn**: Circular reference in Jackson caused StackOverflowError — fixed with @JsonIdentityInfo

## Interview Patterns & Tips
- **ObjectMapper is thread-safe**: can be shared across threads
- **Records**: Jackson supports Java records without annotations
- **Streaming API**: JsonParser for reading, JsonGenerator for writing
- **Custom serializers**: for complex type mappings

## Deep Dive Questions
- **ObjectMapper**: How does Jackson deserialize JSON into Java objects?
- **Streaming vs binding**: When to use each approach?
- **Jackson annotations**: What are the most important annotations?
- **Polymorphism**: How does Jackson handle polymorphic types?
- **Performance**: How to optimize Jackson for high-throughput applications?