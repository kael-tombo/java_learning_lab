# Architecture: String Handling in Java

## String Class Design (Java 9+)
```java
public final class String
    implements java.io.Serializable, Comparable<String>, CharSequence,
               Constable, ConstantDesc {
    
    @Stable
    private final byte[] value;   // Character data
    private final byte coder;     // LATIN1=0 or UTF16=1
    private int hash;             // Cached hash code
    private static final long serialVersionUID = -6849794470754667710L;
}
```

## String Hierarchy
```
CharSequence
├── String (immutable, permanent)
├── StringBuilder (mutable, non-synchronized)
└── StringBuffer (mutable, synchronized, thread-safe)
```

## String Usage in the JDK
Strings are used pervasively:
- **Class names**: Fully qualified class names are Strings
- **System properties**: All property keys/values are Strings
- **Reflection**: Method names, field names are Strings
- **Logging**: Messages are Strings
- **Serialization**: Class descriptors are Strings
- **Resource bundles**: Keys and values are Strings

## String in Modern Java

### Text Blocks (Java 13+)
```java
String json = """
    {
        "name": "Alice",
        "age": 30
    }
    """;
```

### String Interpolation (JDK 21–22 preview, withdrawn before JDK 23)
String Templates were previewed in JDK 21/22 and then withdrawn before JDK 23 — no current JDK accepts the `STR."..."` syntax, even with `--enable-preview`. The same result with `String.formatted`:
```java
String message = "Hello %s, you are %d years old".formatted(name, age);
```
Conceptually, `formatted` keeps the fragments/values split the withdrawn preview taught: the format string holds the literal pieces, the arguments are the interpolated values.

### Record Patterns with Strings
```java
if (obj instanceof String s && s.length() > 5) {
    System.out.println(s.toUpperCase());
}
```

## Architectural Decisions
- **Immutable**: Thread-safe, can be cached, used as HashMap keys
- **Final class**: Cannot be subclassed (security, invariants)
- **Serializable**: Strings survive serialization natively
- **Comparable**: Natural ordering for sorting
- **CharSequence interface**: Interoperable with StringBuilder, CharBuffer, etc.
- **Compact representation**: Memory-efficient for common Latin-1 text
