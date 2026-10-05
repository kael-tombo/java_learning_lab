# THEORY — Serialization Deep Dive

## Overview

Java serialization mechanisms: built-in, JSON, binary protocols, schema evolution, and performance.

---

## Built-in Java Serialization

### Basic Usage

```java
// Serializable marker interface
public class User implements Serializable {
    private static final long serialVersionUID = 1L;
    private String name;
    private transient String password;  // Not serialized
    private Address address;
    
    // Custom serialization
    private void writeObject(ObjectOutputStream out) throws IOException {
        out.defaultWriteObject();
        out.writeObject(encrypt(password));
    }
    
    private void readObject(ObjectInputStream in) throws IOException, ClassNotFoundException {
        in.defaultReadObject();
        password = decrypt((String) in.readObject());
    }
}

// Serialize
try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("user.ser"))) {
    oos.writeObject(user);
}

// Deserialize
try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream("user.ser"))) {
    User user = (User) ois.readObject();
}
```

### Externalizable (Full Control)

```java
public class User implements Externalizable {
    private String name;
    private int age;
    
    public User() {}  // Required
    
    @Override
    public void writeExternal(ObjectOutput out) throws IOException {
        out.writeUTF(name);
        out.writeInt(age);
    }
    
    @Override
    public void readExternal(ObjectInput in) throws IOException, ClassNotFoundException {
        name = in.readUTF();
        age = in.readInt();
    }
}
```

### serialVersionUID

```java
// Explicit (recommended)
private static final long serialVersionUID = 1L;

// Computed if not declared - changes with class structure
// Use serialver tool to generate
```

---

## JSON Serialization

### Jackson (Standard)

```java
ObjectMapper mapper = new ObjectMapper()
    .configure(SerializationFeature.INDENT_OUTPUT, true)
    .registerModule(new JavaTimeModule())
    .configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);

// Serialize
String json = mapper.writeValueAsString(user);

// Deserialize
User user = mapper.readValue(json, User.class);
List<User> users = mapper.readValue(json, new TypeReference<List<User>>() {});

// Annotations
public class User {
    @JsonProperty("full_name")
    private String name;
    
    @JsonIgnore
    private String password;
    
    @JsonFormat(pattern = "yyyy-MM-dd")
    private LocalDate birthDate;
    
    @JsonInclude(JsonInclude.Include.NON_NULL)
    private String nickname;
}
```

### Jackson Configuration

```java
ObjectMapper mapper = new ObjectMapper()
    .setSerializationInclusion(JsonInclude.Include.NON_EMPTY)
    .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS)
    .enable(DeserializationFeature.READ_UNKNOWN_ENUM_VALUES_AS_NULL)
    .configure(MapperFeature.ACCEPT_CASE_INSENSITIVE_PROPERTIES, true);
```

### Jackson Modules

```java
// Java 8 date/time
.registerModule(new JavaTimeModule())

// JSR-310 (Java 8+)
.registerModule(new Jdk8Module())

// Parameter names (constructor injection)
.registerModule(new ParameterNamesModule(JsonCreator.Mode.PROPERTIES))

// Kotlin
.registerModule(new KotlinModule())
```

---

## Binary Protocols

### Protocol Buffers (protobuf)

```protobuf
// user.proto
syntax = "proto3";

message User {
    string id = 1;
    string name = 2;
    int32 age = 3;
    Address address = 4;
    repeated String tags = 5;
    map<string, string> metadata = 6;
}

message Address {
    string street = 1;
    string city = 2;
    string zip = 3;
}
```

```java
// Generated code usage
User user = User.newBuilder()
    .setId("123")
    .setName("Alice")
    .setAge(30)
    .setAddress(Address.newBuilder().setCity("NYC").build())
    .addTags("vip")
    .putMetadata("source", "web")
    .build();

byte[] bytes = user.toByteArray();
User parsed = User.parseFrom(bytes);
```

### Avro

```json
// user.avsc
{
    "type": "record",
    "name": "User",
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "name", "type": "string"},
        {"name": "age", "type": "int"},
        {"name": "address", "type": "Address"}
    ]
}
```

```java
// Schema evolution - add field with default
{"name": "nickname", "type": ["null", "string"], "default": null}
```

### MessagePack

```java
// Compact binary JSON
ObjectMapper mapper = new ObjectMapper(new MessagePackFactory());
byte[] bytes = mapper.writeValueAsBytes(user);
User parsed = mapper.readValue(bytes, User.class);
```

---

## Schema Evolution

### Compatibility Rules

| Change | Forward | Backward |
|--------|---------|----------|
| Add optional field | ✅ | ✅ |
| Remove field | ✅ | ⚠️ |
| Change field type | ❌ | ❌ |
| Rename field | ❌ | ❌ |
| Change field number (protobuf) | ❌ | ❌ |
| Add enum value | ✅ | ⚠️ |

### Jackson Versioning

```java
@JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "type")
@JsonSubTypes({
    @JsonSubTypes.Type(value = UserV1.class, name = "v1"),
    @JsonSubTypes.Type(value = UserV2.class, name = "v2")
})
interface User {}

@JsonTypeName("v1")
class UserV1 implements User { String name; }

@JsonTypeName("v2")
class UserV2 implements User { 
    String name; 
    String email;  // New field
}
```

---

## Custom Serialization

### Kryo (High Performance)

```java
Kryo kryo = new Kryo();
kryo.register(User.class);
kryo.register(Address.class);

Output output = new Output(new FileOutputStream("user.kryo"));
kryo.writeObject(output, user);
output.close();

Input input = new Input(new FileInputStream("user.kryo"));
User user = kryo.readObject(input, User.class);
```

### FST (Fast Serialization)

```java
FSTConfiguration conf = FSTConfiguration.createDefaultConfiguration();
byte[] bytes = conf.asByteArray(user);
User parsed = conf.asObject(bytes);
```

---

## Performance Comparison

| Format | Size | Serialize | Deserialize | Schema |
|--------|------|-----------|-------------|--------|
| Java Built-in | Large | Slow | Slow | Implicit |
| JSON (Jackson) | Medium | Fast | Fast | Optional |
| Protobuf | Small | Very Fast | Very Fast | Required |
| Avro | Small | Fast | Fast | Required |
| MessagePack | Small | Fast | Fast | Optional |
| Kryo | Small | Very Fast | Very Fast | Optional |
| FST | Small | Very Fast | Very Fast | Optional |

---

## Security

### Deserialization Vulnerabilities

```java
// DANGEROUS - arbitrary code execution
ObjectInputStream ois = new ObjectInputStream(input);
Object obj = ois.readObject();  // Can execute arbitrary code!

// Safe alternatives:
// 1. Use JSON (no code execution)
// 2. Use ObjectInputFilter (Java 9+)
ObjectInputStream ois = new ObjectInputStream(input);
ois.setObjectInputFilter(info -> {
    if (info.serialClass() == User.class) return Status.ALLOWED;
    return Status.REJECTED;
});

// 3. Validate before deserializing
// 4. Use allow-lists
```

---

## Best Practices

1. **Prefer JSON** for inter-service communication
2. **Use Protobuf/Avro** for high-performance internal services
3. **Always declare serialVersionUID**
4. **Use transient** for sensitive/derived fields
5. **Implement Externalizable** for complex objects
6. **Filter deserialization** with ObjectInputFilter
7. **Test schema evolution** in CI/CD
8. **Benchmark** your specific use case