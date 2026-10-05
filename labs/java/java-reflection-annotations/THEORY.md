# THEORY — Reflection & Annotations

## Overview

Reflection enables runtime inspection of classes, methods, fields. Annotations provide metadata for frameworks and tools.

---

## Reflection API (java.lang.reflect)

### Class Inspection

```java
Class<?> clazz = MyClass.class;           // From type
Class<?> clazz = obj.getClass();          // From instance
Class<?> clazz = Class.forName("pkg.MyClass"); // From name

// Modifiers
int mods = clazz.getModifiers();
Modifier.isPublic(mods);
Modifier.isAbstract(mods);
Modifier.isFinal(mods);

// Hierarchy
Class<?> superClass = clazz.getSuperclass();
Class<?>[] interfaces = clazz.getInterfaces();
Package pkg = clazz.getPackage();
```

### Members

```java
// Fields
Field[] fields = clazz.getDeclaredFields();  // All declared
Field[] fields = clazz.getFields();          // Public only (incl. inherited)
Field field = clazz.getDeclaredField("name");
field.setAccessible(true);  // Bypass private
Object value = field.get(obj);
field.set(obj, newValue);

// Methods
Method[] methods = clazz.getDeclaredMethods();
Method method = clazz.getDeclaredMethod("compute", int.class, String.class);
method.setAccessible(true);
Object result = method.invoke(instance, 42, "arg");

// Constructors
Constructor<?>[] ctors = clazz.getDeclaredConstructors();
Constructor<?> ctor = clazz.getDeclaredConstructor(String.class, int.class);
ctor.setAccessible(true);
Object instance = ctor.newInstance("name", 42);
```

### Generics via Reflection

```java
// Type tokens (super type tokens)
TypeReference<List<String>> ref = new TypeReference<List<String>>() {};
ParameterizedType type = (ParameterizedType) ref.getType();
Type[] args = type.getActualTypeArguments(); // [String.class]

// Method generic return
Method method = clazz.getMethod("getList");
Type genericReturn = method.getGenericReturnType();
if (genericReturn instanceof ParameterizedType pt) {
    Type arg = pt.getActualTypeArguments()[0];
}
```

### Annotations at Runtime

```java
@Retention(RUNTIME) @Target(TYPE)
@interface Entity { String table() default ""; }

@Entity(table = "users")
class User { }

// Read
Annotation[] annotations = clazz.getAnnotations();
Entity entity = clazz.getAnnotation(Entity.class);
String table = entity.table();
```

---

## Annotations

### Built-in Annotations

| Annotation | Target | Purpose |
|------------|--------|---------|
| `@Override` | METHOD | Override check |
| `@Deprecated` | All | Mark deprecated |
| `@SuppressWarnings` | All | Suppress compiler warnings |
| `@SafeVarargs` | METHOD | Heap pollution safe |
| `@FunctionalInterface` | TYPE | Single abstract method |
| `@Native` | FIELD | Native constant |

### Meta-Annotations

```java
@Retention(RetentionPolicy.RUNTIME)   // SOURCE, CLASS, RUNTIME
@Target(ElementType.TYPE)             // TYPE, FIELD, METHOD, PARAMETER, etc.
@Documented                           // Include in Javadoc
@Inherited                            // Inherit to subclasses
@Repeatable(AuthorList.class)         // Allow multiple
@interface Author {
    String name();
    String email() default "";
}

@Author(name = "A")
@Author(name = "B")
class MyClass { }
```

### Annotation Processing (Compile-time)

```java
// Processor skeleton
@SupportedAnnotationTypes("com.example.Entity")
@SupportedSourceVersion(SourceVersion.RELEASE_21)
public class EntityProcessor extends AbstractProcessor {
    
    @Override
    public boolean process(Set<? extends TypeElement> annotations, 
                          RoundEnvironment roundEnv) {
        for (Element elem : roundEnv.getElementsAnnotatedWith(Entity.class)) {
            // Generate code, validate, etc.
            TypeElement clazz = (TypeElement) elem;
            String table = clazz.getAnnotation(Entity.class).table();
            // Write generated source via Filer
        }
        return true;
    }
}
```

### Common Frameworks

| Framework | Annotations | Processing |
|-----------|-------------|------------|
| Spring | @Component, @Autowired, @Transactional | Runtime (reflection) |
| JPA | @Entity, @Id, @Column, @ManyToOne | Runtime + build |
| Jackson | @JsonProperty, @JsonIgnore | Runtime |
| Lombok | @Data, @Builder, @Value | Compile-time (AST) |
| MapStruct | @Mapper | Compile-time |
| Micronaut | @Inject, @Controller | Compile-time |

---

## MethodHandles & invokedynamic

### MethodHandle Basics

```java
MethodHandles.Lookup lookup = MethodHandles.lookup();
MethodHandle getter = lookup.findGetter(MyClass.class, "name", String.class);
MethodHandle setter = lookup.findSetter(MyClass.class, "name", String.class);
MethodHandle method = lookup.findVirtual(MyClass.class, "compute", 
    MethodType.methodType(int.class, int.class));

// Invoke
String name = (String) getter.invokeExact(obj);
setter.invokeExact(obj, "newName");
int result = (int) method.invokeExact(obj, 42);
```

### invokedynamic

```java
// Bootstrap method creates CallSite
static CallSite bootstrap(MethodHandles.Lookup lookup, 
                          String name, MethodType type) {
    MethodHandle target = lookup.findStatic(Helper.class, "impl", type);
    return new ConstantCallSite(target);
}

// Bytecode: invokedynamic #bootstrap, "compute", (I)I
// Used by: lambdas, string concat, switch, records
```

### Performance

| Invocation | Overhead |
|------------|----------|
| Direct call | Baseline |
| MethodHandle.invokeExact | ~1-2x |
| MethodHandle.invoke | ~2-5x |
| Reflection | ~10-50x |
| Lambda (invokedynamic) | ~Direct (after JIT) |

---

## Modern Alternatives

### VarHandles (Java 9+)

```java
// Atomic, volatile, ordered access
static final VarHandle COUNTER = MethodHandles.varHandle(
    MyClass.class, "counter", int.class
);

COUNTER.getAndAdd(this, 1);          // atomic
COUNTER.compareAndSet(this, 0, 1);   // CAS
COUNTER.getVolatile(this);           // volatile read
COUNTER.setRelease(this, 1);         // release store
```

### Records & Pattern Matching

```java
// No reflection needed for record components
record Person(String name, int age) { }

// Pattern matching replaces reflection-based visitors
switch (obj) {
    case Person(var name, var age) -> ...
}
```

---

## Best Practices

1. **Avoid reflection** in hot paths
2. **Cache** `Method`, `Field`, `Constructor` objects
3. **Use `setAccessible(true)` sparingly** (module restrictions in JPMS)
4. **Prefer compile-time annotation processing** over runtime reflection
5. **Use MethodHandles** for dynamic invocation
6. **Consider VarHandles** for concurrent field access