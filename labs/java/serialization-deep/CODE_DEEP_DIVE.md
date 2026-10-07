# Code Deep Dive - Deep Serialization (serialization-deep)

Six topics, each with a short mechanism note, a complete snippet, the output observed when it was run, and one pitfall.

Conventions used in this file:

- A snippet whose first line is not a `// Requires ...` comment uses only the JDK. It was extracted from this file, compiled with `javac --release 21 -proc:none`, run on JDK 23, and its output pasted verbatim.
- A snippet starting with `// Requires <artifact>; not compiled in this repo` needs a third-party library. It has no observed output.
- Where a library is involved, a JDK-only snippet next to it reproduces the underlying mechanism (reflection-based binding, zigzag varints, tagged fields) so that the idea can still be observed.
- Snippet 1 compiles two versions of a class at run time with `javax.tools` (available in any JDK), so it must be run with a JDK, not a JRE.

## Snippet 1: Serializable & serialVersionUID

Java serialization writes the class descriptor (name, `serialVersionUID`, field names and types) into the stream, and on read compares it with the local class. If the UID differs, `InvalidClassException` is thrown. When a class does not declare `serialVersionUID`, the JVM computes one by hashing the class name, modifiers, interfaces, fields, constructors and methods, so almost any edit changes it. When the UID is declared and matches, the reader maps fields by name, leaves fields that are missing from the stream at their default value, and rejects a field whose type changed.

The demo writes an instance with one compiled version of `Person` and reads it with a second compiled version loaded by a different class loader, for four kinds of change.

```java
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InvalidClassException;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.ObjectStreamClass;
import java.net.URL;
import java.net.URLClassLoader;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.stream.Stream;
import javax.tools.JavaCompiler;
import javax.tools.ToolProvider;

public class EvolvingClassDemo {

    static final String PLAIN_V1 = """
            public class Person implements java.io.Serializable {
                String name = "ada";
                public String toString() { return "Person[name=" + name + "]"; }
                public static Object create() { return new Person(); }
            }
            """;

    static final String PLAIN_V2 = """
            public class Person implements java.io.Serializable {
                String name = "ada";
                int age = 36;
                public String toString() { return "Person[name=" + name + ", age=" + age + "]"; }
                public static Object create() { return new Person(); }
            }
            """;

    static final String PINNED_V1 = """
            public class Person implements java.io.Serializable {
                private static final long serialVersionUID = 1L;
                String name = "ada";
                public String toString() { return "Person[name=" + name + "]"; }
                public static Object create() { return new Person(); }
            }
            """;

    static final String PINNED_V2 = """
            public class Person implements java.io.Serializable {
                private static final long serialVersionUID = 1L;
                String name = "ada";
                int age = 36;
                public String toString() { return "Person[name=" + name + ", age=" + age + "]"; }
                public static Object create() { return new Person(); }
            }
            """;

    static final String PINNED_AGE_INT = """
            public class Person implements java.io.Serializable {
                private static final long serialVersionUID = 1L;
                int age = 36;
                public static Object create() { return new Person(); }
            }
            """;

    static final String PINNED_AGE_STRING = """
            public class Person implements java.io.Serializable {
                private static final long serialVersionUID = 1L;
                String age = "unknown";
                public static Object create() { return new Person(); }
            }
            """;

    static final String RECORD_V1 = """
            public record Person(String name) implements java.io.Serializable {
                public static Object create() { return new Person("ada"); }
            }
            """;

    static final String RECORD_V2 = """
            public record Person(String name, int age) implements java.io.Serializable {
                public static Object create() { return new Person("ada", 36); }
            }
            """;

    static Path compile(String source) throws Exception {
        Path dir = Files.createTempDirectory("evolve");
        Path file = dir.resolve("Person.java");
        Files.writeString(file, source);
        JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
        int status = compiler.run(null, null, null, "-d", dir.toString(), file.toString());
        if (status != 0) {
            throw new IllegalStateException("compilation failed");
        }
        return dir;
    }

    static URLClassLoader loaderFor(Path dir) throws Exception {
        return new URLClassLoader(new URL[] {dir.toUri().toURL()}, ClassLoader.getPlatformClassLoader());
    }

    static void delete(Path dir) throws IOException {
        try (Stream<Path> paths = Files.walk(dir)) {
            paths.sorted(Comparator.reverseOrder()).forEach(p -> p.toFile().delete());
        }
    }

    static String roundTrip(String writerSource, String readerSource) throws Exception {
        Path writerDir = compile(writerSource);
        Path readerDir = compile(readerSource);
        try {
            byte[] bytes;
            try (URLClassLoader writer = loaderFor(writerDir)) {
                Object instance = writer.loadClass("Person").getMethod("create").invoke(null);
                ByteArrayOutputStream buffer = new ByteArrayOutputStream();
                try (ObjectOutputStream out = new ObjectOutputStream(buffer)) {
                    out.writeObject(instance);
                }
                bytes = buffer.toByteArray();
            }
            try (URLClassLoader reader = loaderFor(readerDir);
                    ObjectInputStream in = new ObjectInputStream(new ByteArrayInputStream(bytes)) {
                        @Override
                        protected Class<?> resolveClass(ObjectStreamClass desc) throws IOException, ClassNotFoundException {
                            return Class.forName(desc.getName(), false, reader);
                        }
                    }) {
                return "read OK -> " + in.readObject();
            }
        } catch (InvalidClassException e) {
            return "InvalidClassException: " + e.getMessage();
        } finally {
            delete(writerDir);
            delete(readerDir);
        }
    }

    public static void main(String[] args) throws Exception {
        System.out.println("A) no serialVersionUID, field added");
        System.out.println("   " + roundTrip(PLAIN_V1, PLAIN_V2));
        System.out.println("B) serialVersionUID = 1L pinned, field added");
        System.out.println("   " + roundTrip(PINNED_V1, PINNED_V2));
        System.out.println("C) serialVersionUID = 1L pinned, field 'age' changed from int to String");
        System.out.println("   " + roundTrip(PINNED_AGE_INT, PINNED_AGE_STRING));
        System.out.println("D) record gains a component");
        System.out.println("   " + roundTrip(RECORD_V1, RECORD_V2));
    }
}
```

Observed output (`java EvolvingClassDemo`; the two long numbers in line A are the computed UIDs and depend on the exact class files javac produced here):

```text
A) no serialVersionUID, field added
   InvalidClassException: Person; local class incompatible: stream classdesc serialVersionUID = -515195006988609165, local class serialVersionUID = -4026712693513862765
B) serialVersionUID = 1L pinned, field added
   read OK -> Person[name=ada, age=0]
C) serialVersionUID = 1L pinned, field 'age' changed from int to String
   InvalidClassException: Person; incompatible types for field age
D) record gains a component
   read OK -> Person[name=ada, age=0]
```

Reading the four results: A fails because the computed UIDs differ. B succeeds, but `age` is 0, not 36: deserialization does not run the constructor or field initializers of the serializable class, so a field absent from the stream gets the type's default. C fails even with a matching UID because the descriptor says `age` is a primitive `int` and the local class says `String`. D succeeds because a record is rebuilt through its canonical constructor and records are exempt from the UID comparison; the missing `age` arrives as 0.

**Pitfall:** relying on the computed UID turns a harmless refactor (adding a convenience method, or changing the compiler) into an `InvalidClassException` for every object already persisted in a session store, cache or queue. Pinning the UID fixes that but creates the opposite risk shown in B: old data silently produces objects with default values (`age == 0`) that violate whatever the new code assumes, so a pinned UID must come with a `readObject` that validates or fills in new fields. Separately, `ObjectInputStream.readObject` on untrusted bytes can instantiate arbitrary serializable classes on the classpath; set an `ObjectInputFilter` (for example via `ObjectInputStream.setObjectInputFilter`) that allow-lists the expected classes.

## Snippet 2: Externalizable

`Externalizable` hands the entire wire format to you: `writeExternal(ObjectOutput)` and `readExternal(ObjectInput)` replace the default field-by-field protocol, and only the class name (not the fields) is written as metadata. On read, the JVM calls the class's public no-argument constructor first and then `readExternal`, which is the opposite of plain `Serializable`, where no constructor of the class itself runs. The result is smaller and faster, but you own field order and versioning.

```java
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.Externalizable;
import java.io.IOException;
import java.io.InvalidClassException;
import java.io.InvalidObjectException;
import java.io.ObjectInput;
import java.io.ObjectInputStream;
import java.io.ObjectOutput;
import java.io.ObjectOutputStream;
import java.io.Serializable;

public class ExternalizableDemo {

    static class Plain implements Serializable {
        private static final long serialVersionUID = 1L;
        int id;
        String name;
        double score;

        Plain(int id, String name, double score) {
            System.out.println("  Plain constructor ran");
            this.id = id;
            this.name = name;
            this.score = score;
        }
    }

    public static class Compact implements Externalizable {
        int id;
        String name;
        double score;

        public Compact() {
            System.out.println("  Compact public no-arg constructor ran");
        }

        Compact(int id, String name, double score) {
            this.id = id;
            this.name = name;
            this.score = score;
        }

        @Override
        public void writeExternal(ObjectOutput out) throws IOException {
            out.writeByte(1); // our own format version
            out.writeInt(id);
            out.writeUTF(name);
            out.writeDouble(score);
        }

        @Override
        public void readExternal(ObjectInput in) throws IOException {
            int version = in.readByte();
            if (version != 1) {
                throw new InvalidObjectException("unknown format version " + version);
            }
            id = in.readInt();
            name = in.readUTF();
            score = in.readDouble();
        }
    }

    public static class Hidden implements Externalizable {
        Hidden() { // not public: unusable for Externalizable
        }

        @Override
        public void writeExternal(ObjectOutput out) throws IOException {
            out.writeInt(7);
        }

        @Override
        public void readExternal(ObjectInput in) throws IOException {
            in.readInt();
        }
    }

    static byte[] write(Object o) throws IOException {
        ByteArrayOutputStream buffer = new ByteArrayOutputStream();
        try (ObjectOutputStream out = new ObjectOutputStream(buffer)) {
            out.writeObject(o);
        }
        return buffer.toByteArray();
    }

    static Object read(byte[] bytes) throws IOException, ClassNotFoundException {
        try (ObjectInputStream in = new ObjectInputStream(new ByteArrayInputStream(bytes))) {
            return in.readObject();
        }
    }

    public static void main(String[] args) throws Exception {
        System.out.println("writing");
        byte[] plain = write(new Plain(7, "ada", 9.5));
        byte[] compact = write(new Compact(7, "ada", 9.5));
        System.out.println("Serializable bytes   = " + plain.length);
        System.out.println("Externalizable bytes = " + compact.length);

        System.out.println("reading Plain");
        Plain p = (Plain) read(plain);
        System.out.println("  got id=" + p.id + " name=" + p.name + " score=" + p.score);

        System.out.println("reading Compact");
        Compact c = (Compact) read(compact);
        System.out.println("  got id=" + c.id + " name=" + c.name + " score=" + c.score);

        byte[] hidden = write(new Hidden());
        try {
            read(hidden);
        } catch (InvalidClassException e) {
            System.out.println("reading Hidden -> InvalidClassException: " + e.getMessage());
        }
    }
}
```

Observed output (`java ExternalizableDemo`):

```text
writing
  Plain constructor ran
Serializable bytes   = 104
Externalizable bytes = 68
reading Plain
  got id=7 name=ada score=9.5
reading Compact
  Compact public no-arg constructor ran
  got id=7 name=ada score=9.5
reading Hidden -> InvalidClassException: ExternalizableDemo$Hidden; no valid constructor
```

**Pitfall:** `Externalizable` classes need a public no-argument constructor, and a missing one is only discovered when reading: writing `Hidden` succeeded, reading it threw `InvalidClassException ... no valid constructor`, so the failure shows up in whichever service consumes the data, not where it was produced. A second trap is the format itself: `readExternal` must consume exactly what `writeExternal` produced, in the same order, and nothing in the stream names the fields, so inserting a new field in the middle makes old data decode as shifted garbage. The leading version byte in `Compact` is the minimum protection.

## Snippet 3: Jackson databind

Jackson's `ObjectMapper` builds a model of each class by reflection (constructors, getters, fields, annotations, and since 2.12 record components), then streams JSON tokens to or from it. Its defaults are strict on reading, so an unknown JSON property fails with `UnrecognizedPropertyException` unless you turn off `FAIL_ON_UNKNOWN_PROPERTIES` or annotate the type with `@JsonIgnoreProperties(ignoreUnknown = true)`. Dates need the `JavaTimeModule`, and polymorphic types need explicit type metadata.

```java
// Requires com.fasterxml.jackson.core:jackson-databind (2.12+ for records; 2.15+ is safest when renaming record properties) and com.fasterxml.jackson.datatype:jackson-datatype-jsr310; not compiled in this repo
import com.fasterxml.jackson.annotation.JsonIgnoreProperties;
import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.annotation.JsonSubTypes;
import com.fasterxml.jackson.annotation.JsonTypeInfo;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.SerializationFeature;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import java.time.Instant;
import java.util.List;

public class JacksonDemo {

    record Order(@JsonProperty("order_id") long id, String customer, Instant placedAt) {}

    @JsonIgnoreProperties(ignoreUnknown = true)
    record LenientOrder(long id, String customer) {}

    @JsonTypeInfo(use = JsonTypeInfo.Id.NAME, property = "type")
    @JsonSubTypes({
            @JsonSubTypes.Type(value = Dog.class, name = "dog"),
            @JsonSubTypes.Type(value = Cat.class, name = "cat")
    })
    sealed interface Pet permits Dog, Cat {}

    record Dog(String name) implements Pet {}

    record Cat(String name, int lives) implements Pet {}

    public static void main(String[] args) throws Exception {
        ObjectMapper mapper = new ObjectMapper()
                .registerModule(new JavaTimeModule())
                .disable(SerializationFeature.WRITE_DATES_AS_TIMESTAMPS);

        String json = mapper.writeValueAsString(new Order(1L, "ada", Instant.parse("2024-01-01T00:00:00Z")));
        System.out.println(json); // {"customer":"ada","placedAt":"2024-01-01T00:00:00Z","order_id":1}  (property order may differ)

        Order back = mapper.readValue(json, Order.class);
        List<Order> many = mapper.readValue("[" + json + "," + json + "]", new TypeReference<List<Order>>() {});
        System.out.println(back + " / " + many.size());

        // unknown property from a newer producer: fails by default, tolerated by annotation or feature flag
        String fromNewerProducer = "{\"id\":1,\"customer\":\"ada\",\"coupon\":\"X1\"}";
        LenientOrder lenient = mapper.readValue(fromNewerProducer, LenientOrder.class);
        ObjectMapper tolerant = mapper.copy().configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);

        String petJson = mapper.writeValueAsString(new Cat("tom", 9)); // includes "type":"cat"
        Pet pet = mapper.readValue(petJson, Pet.class);
        System.out.println(lenient + " " + tolerant.readValue(fromNewerProducer, LenientOrder.class) + " " + pet);
    }
}
```

JDK-only miniature of the reflection step (binding `key=value` text onto a record through its components, strict versus tolerant on unknown keys):

```java
import java.lang.reflect.Constructor;
import java.lang.reflect.RecordComponent;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

public class ReflectiveBinderDemo {

    record Customer(String name, int age, boolean vip) {}

    static <T extends Record> T bind(Class<T> type, String input, boolean failOnUnknown) throws Exception {
        Map<String, String> values = new HashMap<>();
        for (String pair : input.split(";")) {
            String[] kv = pair.split("=", 2);
            values.put(kv[0], kv[1]);
        }

        RecordComponent[] components = type.getRecordComponents();
        Object[] args = new Object[components.length];
        Class<?>[] types = new Class<?>[components.length];
        Set<String> unknown = new HashSet<>(values.keySet());

        for (int i = 0; i < components.length; i++) {
            RecordComponent c = components[i];
            types[i] = c.getType();
            String raw = values.get(c.getName());
            unknown.remove(c.getName());
            if (raw == null) {
                args[i] = types[i] == int.class ? 0 : types[i] == boolean.class ? false : null;
            } else if (types[i] == int.class) {
                args[i] = Integer.parseInt(raw);
            } else if (types[i] == boolean.class) {
                args[i] = Boolean.parseBoolean(raw);
            } else {
                args[i] = raw;
            }
        }

        if (failOnUnknown && !unknown.isEmpty()) {
            throw new IllegalArgumentException("Unrecognized property " + new java.util.TreeSet<>(unknown)
                    + " for " + type.getSimpleName() + ", known: " + Arrays.stream(components).map(RecordComponent::getName).toList());
        }
        Constructor<T> constructor = type.getDeclaredConstructor(types);
        return constructor.newInstance(args);
    }

    public static void main(String[] args) throws Exception {
        String fromNewerProducer = "name=ada;age=36;coupon=X1";
        System.out.println("tolerant: " + bind(Customer.class, fromNewerProducer, false));
        try {
            bind(Customer.class, fromNewerProducer, true);
        } catch (IllegalArgumentException e) {
            System.out.println("strict:   " + e.getMessage());
        }
        System.out.println("missing:  " + bind(Customer.class, "name=bob", false));
    }
}
```

Observed output (`java ReflectiveBinderDemo`):

```text
tolerant: Customer[name=ada, age=36, vip=false]
strict:   Unrecognized property [coupon] for Customer, known: [name, age, vip]
missing:  Customer[name=bob, age=0, vip=false]
```

**Pitfall:** the strict default is a deployment-ordering trap. If producer B ships a new JSON property before consumer A is upgraded, every message A reads fails with `UnrecognizedPropertyException`, which is the strict line above. The opposite switch has its own cost: with `FAIL_ON_UNKNOWN_PROPERTIES` off, a misspelled property in a request is dropped silently, and a missing one becomes `0`/`null`/`false` exactly like the `missing:` line above. Separately, never combine `enableDefaultTyping` (or `@JsonTypeInfo(use = Id.CLASS)`) with untrusted input: it lets the payload choose the class to instantiate, a documented source of deserialization remote-code-execution CVEs.

## Snippet 4: Avro schemas

Avro's binary encoding contains no field names and no tags: a record is just its fields' values concatenated in schema order, with `long`/`int` as zigzag varints and `string` as a zigzag length followed by UTF-8. The bytes are therefore meaningless without the schema that wrote them, and schema evolution works by giving the reader both the writer's schema and its own, then resolving fields by name (a reader field missing from the writer needs a `default`).

```java
// Requires org.apache.avro:avro; not compiled in this repo
import java.io.ByteArrayOutputStream;
import org.apache.avro.Schema;
import org.apache.avro.SchemaCompatibility;
import org.apache.avro.generic.GenericData;
import org.apache.avro.generic.GenericDatumReader;
import org.apache.avro.generic.GenericDatumWriter;
import org.apache.avro.generic.GenericRecord;
import org.apache.avro.io.BinaryEncoder;
import org.apache.avro.io.Decoder;
import org.apache.avro.io.DecoderFactory;
import org.apache.avro.io.EncoderFactory;

public class AvroDemo {

    static final String V1 = """
            {"type":"record","name":"User","namespace":"demo","fields":[
              {"name":"id","type":"long"},
              {"name":"name","type":"string"}]}
            """;

    static final String V2 = """
            {"type":"record","name":"User","namespace":"demo","fields":[
              {"name":"id","type":"long"},
              {"name":"name","type":"string"},
              {"name":"email","type":["null","string"],"default":null}]}
            """;

    public static void main(String[] args) throws Exception {
        Schema writerSchema = new Schema.Parser().parse(V1);
        Schema readerSchema = new Schema.Parser().parse(V2);

        GenericRecord user = new GenericData.Record(writerSchema);
        user.put("id", 150L);
        user.put("name", "ada");

        ByteArrayOutputStream out = new ByteArrayOutputStream();
        BinaryEncoder encoder = EncoderFactory.get().binaryEncoder(out, null);
        new GenericDatumWriter<GenericRecord>(writerSchema).write(user, encoder);
        encoder.flush();

        Decoder decoder = DecoderFactory.get().binaryDecoder(out.toByteArray(), null);
        GenericRecord upgraded = new GenericDatumReader<GenericRecord>(writerSchema, readerSchema).read(null, decoder);
        System.out.println(upgraded); // email takes its default, null

        System.out.println(SchemaCompatibility.checkReaderWriterCompatibility(readerSchema, writerSchema).getType());
    }
}
```

JDK-only demonstration of the wire format, including what happens when the reader uses the wrong schema:

```java
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;

public class AvroWireFormatDemo {

    static void writeLong(ByteArrayOutputStream out, long value) {
        long zigzag = (value << 1) ^ (value >> 63);
        while ((zigzag & ~0x7FL) != 0) {
            out.write((int) ((zigzag & 0x7F) | 0x80));
            zigzag >>>= 7;
        }
        out.write((int) zigzag);
    }

    static void writeString(ByteArrayOutputStream out, String s) {
        byte[] utf8 = s.getBytes(StandardCharsets.UTF_8);
        writeLong(out, utf8.length);
        out.write(utf8, 0, utf8.length);
    }

    static final class Reader {
        private final byte[] data;
        private int pos;

        Reader(byte[] data) {
            this.data = data;
        }

        long readLong() {
            long raw = 0;
            int shift = 0;
            while (true) {
                int b = data[pos++] & 0xFF;
                raw |= (long) (b & 0x7F) << shift;
                if ((b & 0x80) == 0) {
                    break;
                }
                shift += 7;
            }
            return (raw >>> 1) ^ -(raw & 1);
        }

        String readString() {
            long length = readLong();
            if (length < 0 || length > data.length - pos) {
                throw new IllegalStateException("string length " + length + " but only " + (data.length - pos) + " bytes remain");
            }
            String s = new String(data, pos, (int) length, StandardCharsets.UTF_8);
            pos += (int) length;
            return s;
        }
    }

    static String hex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x ", b));
        }
        return sb.toString().trim();
    }

    public static void main(String[] args) {
        // writer schema: record User { long id; string name; }
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        writeLong(out, 150);
        writeString(out, "ada");
        byte[] bytes = out.toByteArray();
        System.out.println("encoded " + bytes.length + " bytes: " + hex(bytes));

        Reader right = new Reader(bytes);
        System.out.println("read with writer schema (long, string): id=" + right.readLong() + " name=" + right.readString());

        System.out.println("zigzag(0)=" + zigzagBytes(0) + " zigzag(-1)=" + zigzagBytes(-1) + " zigzag(1)=" + zigzagBytes(1) + " zigzag(-64)=" + zigzagBytes(-64));

        try {
            Reader wrong = new Reader(bytes);
            System.out.println("read with wrong schema (string, long): name=" + wrong.readString());
        } catch (IllegalStateException e) {
            System.out.println("read with wrong schema (string, long): " + e.getMessage());
        }
    }

    static String zigzagBytes(long v) {
        ByteArrayOutputStream o = new ByteArrayOutputStream();
        writeLong(o, v);
        return hex(o.toByteArray());
    }
}
```

Observed output (`java AvroWireFormatDemo`):

```text
encoded 6 bytes: ac 02 06 61 64 61
read with writer schema (long, string): id=150 name=ada
zigzag(0)=00 zigzag(-1)=01 zigzag(1)=02 zigzag(-64)=7f
read with wrong schema (string, long): string length 150 but only 4 bytes remain
```

**Pitfall:** adding a field to the reader's schema without a `default` breaks reading of every record already written, because resolution has nothing to supply for the missing field; Avro fails with an `AvroTypeException` rather than inventing a value. The inverse mistake is shown by the last line above: since the stream carries no field names, a reader that is handed the wrong writer schema (for example a schema fetched by an out-of-date id) either throws a length error like this one or, when the bytes happen to be plausible, silently decodes nonsense. Always ship or look up the writer schema with the data (container files embed it; Kafka setups use a schema-registry id).

## Snippet 5: Protobuf

A protobuf message is a sequence of (key, value) pairs; the key is a varint holding `(field_number << 3) | wire_type`, so what identifies a field on the wire is its number, never its name. Unknown field numbers are skipped by wire type, which is what makes adding fields safe in both directions. `int32`/`int64` encode negative numbers as ten-byte varints, while `sint32`/`sint64` zigzag-encode first so small negatives stay short.

```proto
// Requires protoc (com.google.protobuf:protobuf-java for the generated code); not compiled in this repo
syntax = "proto3";
package demo;
option java_package = "demo";
option java_multiple_files = true;

message User {
  int64 id = 1;
  string name = 2;
  reserved 3;          // a removed field: this number can never be reused
  reserved "email";    // and its name is blocked too
  sint32 balance = 4;  // zigzag: small negative numbers stay one byte
}
```

```java
// Requires com.google.protobuf:protobuf-java and the class generated from the .proto above; not compiled in this repo
import com.google.protobuf.InvalidProtocolBufferException;
import demo.User;

public class ProtobufDemo {
    public static void main(String[] args) throws InvalidProtocolBufferException {
        User user = User.newBuilder()
                .setId(150)
                .setName("ada")
                .setBalance(-3)
                .build();

        byte[] bytes = user.toByteArray();
        User back = User.parseFrom(bytes);
        System.out.println(back.getId() + " " + back.getName() + " " + back.getBalance());
    }
}
```

JDK-only encoder for the same wire format (varint, key bytes, the ten-byte negative, and skipping an unknown field):

```java
import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;

public class ProtobufWireDemo {

    static void varint(ByteArrayOutputStream out, long value) {
        while ((value & ~0x7FL) != 0) {
            out.write((int) ((value & 0x7F) | 0x80));
            value >>>= 7;
        }
        out.write((int) value);
    }

    static void key(ByteArrayOutputStream out, int fieldNumber, int wireType) {
        varint(out, ((long) fieldNumber << 3) | wireType);
    }

    static String hex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02x ", b));
        }
        return sb.toString().trim();
    }

    static byte[] encodeVarintField(int fieldNumber, long value) {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        key(out, fieldNumber, 0);
        varint(out, value);
        return out.toByteArray();
    }

    public static void main(String[] args) {
        System.out.println("field 1 = 150 (int64)    : " + hex(encodeVarintField(1, 150)));
        System.out.println("field 1 = -1  (int64)    : " + hex(encodeVarintField(1, -1)));
        long zigzagMinusOne = (-1L << 1) ^ (-1L >> 63);
        System.out.println("field 1 = -1  (sint64)   : " + hex(encodeVarintField(1, zigzagMinusOne)));

        ByteArrayOutputStream out = new ByteArrayOutputStream();
        key(out, 2, 2); // wire type 2 = length-delimited
        byte[] text = "testing".getBytes(StandardCharsets.UTF_8);
        varint(out, text.length);
        out.write(text, 0, text.length);
        System.out.println("field 2 = \"testing\"      : " + hex(out.toByteArray()));

        // A message with fields 1 (varint) and 9 (string); the reader only knows field 1.
        ByteArrayOutputStream msg = new ByteArrayOutputStream();
        msg.writeBytes(encodeVarintField(1, 150));
        key(msg, 9, 2);
        varint(msg, 3);
        msg.writeBytes("new".getBytes(StandardCharsets.UTF_8));
        byte[] bytes = msg.toByteArray();

        int pos = 0;
        while (pos < bytes.length) {
            int k = bytes[pos++] & 0xFF; // keys below 16 fit in one byte
            int field = k >>> 3;
            int wire = k & 7;
            if (wire == 0) {
                long v = 0;
                int shift = 0;
                int b;
                do {
                    b = bytes[pos++] & 0xFF;
                    v |= (long) (b & 0x7F) << shift;
                    shift += 7;
                } while ((b & 0x80) != 0);
                System.out.println("field " + field + " (varint) -> " + v);
            } else if (wire == 2) {
                int length = bytes[pos++] & 0xFF;
                pos += length;
                System.out.println("field " + field + " (length-delimited, " + length + " bytes) -> unknown, skipped");
            }
        }
    }
}
```

Observed output (`java ProtobufWireDemo`):

```text
field 1 = 150 (int64)    : 08 96 01
field 1 = -1  (int64)    : 08 ff ff ff ff ff ff ff ff ff 01
field 1 = -1  (sint64)   : 08 01
field 2 = "testing"      : 12 07 74 65 73 74 69 6e 67
field 1 (varint) -> 150
field 9 (length-delimited, 3 bytes) -> unknown, skipped
```

**Pitfall:** the field number is the contract. Changing `string name = 2;` to `int64 name = 2;` or reusing a deleted number for a new meaning does not fail at parse time; old bytes are re-read under the new meaning (snippet 6 reproduces this with a tagged format). That is why removed fields should be marked `reserved` as in the `.proto` above. Also note the `-1` row: declaring a field that is often negative as `int64` costs ten bytes per value, where `sint64` costs one.

## Snippet 6: versioning & compatibility

Two directions matter. Backward compatibility means new code reads old data (missing fields must have defaults); forward compatibility means old code reads new data (unknown fields must be skippable). Self-describing tagged formats achieve both by writing `id, length, payload` per field: a reader dispatches on `id`, and an id it does not know is skipped using `length`. The demo implements such a format with `DataOutputStream` and exercises both directions, then shows what happens when a tag is reused with a different type.

```java
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.nio.charset.StandardCharsets;

public class TaggedFormatDemo {

    static final int NAME = 1;
    static final int AGE = 2;
    static final int EMAIL = 3;

    static void field(DataOutputStream out, int id, byte[] payload) throws IOException {
        out.writeByte(id);
        out.writeShort(payload.length);
        out.write(payload);
    }

    static byte[] text(String s) {
        return s.getBytes(StandardCharsets.UTF_8);
    }

    static byte[] integer(int v) {
        return new byte[] {(byte) (v >>> 24), (byte) (v >>> 16), (byte) (v >>> 8), (byte) v};
    }

    static byte[] writeV1() throws IOException {
        ByteArrayOutputStream buffer = new ByteArrayOutputStream();
        DataOutputStream out = new DataOutputStream(buffer);
        field(out, NAME, text("ada"));
        field(out, AGE, integer(36));
        return buffer.toByteArray();
    }

    static byte[] writeV2() throws IOException {
        ByteArrayOutputStream buffer = new ByteArrayOutputStream();
        DataOutputStream out = new DataOutputStream(buffer);
        field(out, NAME, text("ada"));
        field(out, AGE, integer(36));
        field(out, EMAIL, text("ada@example.org"));
        return buffer.toByteArray();
    }

    static byte[] writeBrokenV3() throws IOException {
        ByteArrayOutputStream buffer = new ByteArrayOutputStream();
        DataOutputStream out = new DataOutputStream(buffer);
        field(out, NAME, text("ada"));
        field(out, AGE, text("abcd")); // tag 2 reused with a different meaning (4 bytes of text)
        return buffer.toByteArray();
    }

    // knownEmail = false models the v1 reader, true models the v2 reader
    static String read(byte[] bytes, boolean knownEmail) throws IOException {
        DataInputStream in = new DataInputStream(new ByteArrayInputStream(bytes));
        String name = "?";
        int age = -1;
        String email = "(default)";
        String skipped = "";
        while (in.available() > 0) {
            int id = in.readUnsignedByte();
            byte[] payload = new byte[in.readUnsignedShort()];
            in.readFully(payload);
            switch (id) {
                case NAME -> name = new String(payload, StandardCharsets.UTF_8);
                case AGE -> {
                    if (payload.length != 4) {
                        throw new IOException("AGE must be 4 bytes, found " + payload.length);
                    }
                    age = ((payload[0] & 0xFF) << 24) | ((payload[1] & 0xFF) << 16) | ((payload[2] & 0xFF) << 8) | (payload[3] & 0xFF);
                }
                case EMAIL -> {
                    if (knownEmail) {
                        email = new String(payload, StandardCharsets.UTF_8);
                    } else {
                        skipped += " skipped-id-" + id;
                    }
                }
                default -> skipped += " skipped-id-" + id;
            }
        }
        return "name=" + name + " age=" + age + " email=" + email + skipped;
    }

    public static void main(String[] args) throws IOException {
        System.out.println("v1 data, v1 reader : " + read(writeV1(), false));
        System.out.println("v1 data, v2 reader : " + read(writeV1(), true) + "   <- backward compatible");
        System.out.println("v2 data, v1 reader : " + read(writeV2(), false) + "   <- forward compatible");
        System.out.println("v2 data, v2 reader : " + read(writeV2(), true));
        System.out.println("v3 data (tag 2 reused as text), v1 reader : " + read(writeBrokenV3(), false));
    }
}
```

Observed output (`java TaggedFormatDemo`):

```text
v1 data, v1 reader : name=ada age=36 email=(default)
v1 data, v2 reader : name=ada age=36 email=(default)   <- backward compatible
v2 data, v1 reader : name=ada age=36 email=(default) skipped-id-3   <- forward compatible
v2 data, v2 reader : name=ada age=36 email=ada@example.org
v3 data (tag 2 reused as text), v1 reader : name=ada age=1633837924 email=(default)
```

The same rules appear in every library above: Jackson's `ignoreUnknown`, Avro's reader-schema defaults, and protobuf's "never reuse a number, mark it reserved". Native Java serialization offers them only through a pinned `serialVersionUID` plus careful field additions (snippet 1, scenario B).

**Pitfall:** reusing a tag with a new type is the one change a tagged format cannot detect when the sizes happen to line up. In the last line above the v1 reader accepted a four-character string as a four-byte `age` and produced a large nonsense integer, with no exception. The only real defences are process ones: retire ids instead of redefining them, and run a compatibility check (Avro's `SchemaCompatibility`, `buf breaking` for protobuf, or a golden-bytes test that decodes archived payloads from every released version) in CI.

## Verification notes

- Compiled and run (6 total): `EvolvingClassDemo`, `ExternalizableDemo`, `ReflectiveBinderDemo`, `AvroWireFormatDemo`, `ProtobufWireDemo`, `TaggedFormatDemo`, each with `javac --release 21 -proc:none` and `java`.
- Not compiled (need external artifacts): `JacksonDemo`, `AvroDemo`, the `.proto` file and `ProtobufDemo`.
- The UID numbers in `EvolvingClassDemo` line A depend on the class files produced by the JDK 23 compiler in this environment; the other outputs do not.
