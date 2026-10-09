# JSON Serialization — Theoretical Foundation

## Core Concepts

### 1. Fundamental Principle
JSON (JavaScript Object Notation) serialization converts Java objects to and from JSON strings. Unlike Java serialization, JSON is text-based, human-readable, and language-independent.

### 2. Theoretical Foundation
JSON serialization frameworks like Jackson, Gson, and JSON-B provide mapping between Java object graphs and JSON representation. They handle type conversion, nesting, collections, and polymorphic types.

#### Key Theoretical Properties
- **Human Readable**: JSON is text-based and easy to read and debug
- **Schema Optional**: No formal schema required (unless using JSON Schema)
- **Cross-Platform**: JSON is supported in virtually every programming language
- **Performance**: Generally faster than Java serialization, slower than binary formats

### 3. Algorithmic Details

#### Serialization Pipeline (Jackson)
1. ObjectMapper serializes POJO using BeanSerializer
2. BeanSerializer introspects getter methods and fields
3. Property values are converted to JsonToken stream
4. JsonGenerator writes tokens to output (String, File, OutputStream)
5. Custom serializers can intercept specific types

#### Deserialization Pipeline (Jackson)
1. JsonParser reads input as JsonToken stream
2. BeanDeserializer creates target object (often via no-arg constructor)
3. Properties are set via setter methods or direct field access
4. Type information is used for generics and polymorphic types

### 4. Trade-offs

#### Jackson vs Gson vs JSON-B
- **Jackson**: Most features, best performance, extensive annotation support
- **Gson**: Simpler API, good for basic use cases, less configurable
- **JSON-B**: Jakarta EE standard, annotation-driven, portable across implementations

### 5. Mathematical Basis

#### Serialization Complexity
- Object traversal: O(n) where n is number of properties
- String escaping: O(m) where m is string length
- Pretty printing: O(n) additional whitespace

#### Memory Overhead
- Jackson uses token streaming: O(1) memory for streaming API
- Tree model (JsonNode): O(n) memory proportional to document size
- POJO binding: O(n) for deserialized object graph

## Summary
JSON serialization is the dominant format for REST APIs and web services. Understanding the mapping mechanics is crucial for building robust APIs.

## Key Theorems

### Theorem 1: Type Erasure
Generic type information is erased at runtime, requiring TypeReference or TypeFactory for parameterized types.

### Theorem 2: Deserialization Order
Properties can be deserialized in any order — the framework must wait for all required properties before constructing immutable objects.

### Theorem 3: Polymorphic Type Resolution
Polymorphic serialization requires explicit type information (dedicated field, wrapper object) since JSON has no native type discrimination.

## Key Insights

### Insight 1: Annotations Are Powerful
Jackson annotations like @JsonProperty, @JsonIgnore, @JsonFormat provide fine-grained control without modifying business logic.

### Insight 2: Streaming Is More Efficient
For large documents, the streaming API (JsonParser/JsonGenerator) avoids building the full object tree in memory.

### Insight 3: Serialization is Not Serialization
Java object serialization and JSON serialization are fundamentally different — JSON serialization uses public API (getters/setters), while Java serialization accesses private fields directly.
