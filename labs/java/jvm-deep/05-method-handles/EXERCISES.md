# EXERCISES — Method Handles & invokedynamic

## 1. Basic Method Handle Lookup (Beginner)

**Goal**: Look up and invoke various method handles.

```java
// Find and invoke:
MethodHandles.Lookup lookup = MethodHandles.lookup();

// Static method
MethodHandle sqrt = lookup.findStatic(Math.class, "sqrt", 
    MethodType.methodType(double.class, double.class));
double result = (double) sqrt.invokeExact(16.0); // 4.0

// Instance method
MethodHandle substring = lookup.findVirtual(String.class, "substring",
    MethodType.methodType(String.class, int.class, int.class));
String result = (String) substring.invokeExact("hello", 1, 4); // "ell"
```

**Tasks**:
1. Look up and invoke `String.length()` via MethodHandle
2. Look up `ArrayList.add(E)` and invoke on a list
3. Create a MethodHandle for `Integer.parseInt(String)` and test it

---

## 2. MethodHandle Transformations (Intermediate)

**Goal**: Practice MethodHandle transformations.

```java
MethodHandles.Lookup lookup = MethodHandles.lookup();
MethodHandle sqrt = lookup.findStatic(Math.class, "sqrt", 
    MethodType.methodType(double.class, double.class));

// 1. Filter argument: sqrt(x * x)
MethodHandle squared = MethodHandles.filterArguments(sqrt, 0,
    MethodHandles.insertArguments(
        lookup.findStatic(Math.class, "multiplyExact", 
            MethodType.methodType(int.class, int.class, int.class)),
        0, 2  // multiply by 2
    ));

// 2. Bind first argument
MethodHandle sqrtOf2 = sqrt.bindTo(2.0); // sqrt(2.0) = 1.414...
double result = (double) sqrtOf2.invokeExact();

// 3. Spread array to arguments
MethodHandle spread = lookup.findStatic(Arrays.class, "asList",
    MethodType.methodType(List.class, Object[].class))
    .asSpreader(Object[].class, 3);
List<String> list = (List<String>) spread.invokeExact("a", "b", "c");
```

**Tasks**:
1. Create a MethodHandle that doubles its input
2. Create a MethodHandle that takes an int[] and returns sum
3. Use `asSpreader` and `asCollector` for varargs-style handling

---

## 2. Guarded Invocation (Intermediate)

**Goal**: Implement conditional method handle execution.

```java
MethodHandle mh = lookup.findVirtual(String.class, "toUpperCase", 
    MethodType.methodType(String.class));

MethodHandle guard = lookup.findVirtual(String.class, "isEmpty",
    MethodType.methodType(boolean.class));

MethodHandle fallback = MethodHandles.constant(String.class, "EMPTY");

MethodHandle guarded = MethodHandles.guardWithTest(guard, mh, fallback);

// Test
assert "HELLO".equals(guarded.invokeExact("hello"));
assert "EMPTY".equals(guarded.invokeExact(""));
```

**Tasks**:
1. Create a guarded MethodHandle that returns "N/A" for null inputs
2. Chain multiple guards with different conditions

---

## 3. Lambda & invokedynamic (Advanced)

**Goal**: Understand lambda compilation.

```java
// This lambda:
Runnable r = () -> System.out.println("hello");

// Compiles to invokedynamic:
// Bootstrap: LambdaMetafactory.metafactory
// Static args: (Ljava/lang/Runnable;)V, ()V, ()V
// Dynamic args: captured variables (none here)

// Manual equivalent:
MethodHandle impl = lookup.findVirtual(
    MyClass.class, "lambda$0", MethodType.methodType(void.class));
CallSite site = LambdaMetafactory.metafactory(
    lookup, "run", MethodType.methodType(Runnable.class),
    MethodType.methodType(void.class), impl, MethodType.methodType(void.class));
Runnable r = (Runnable) site.getTarget().invokeExact();
```

**Tasks**:
1. Write a program that uses `LambdaMetafactory` to create a `Comparator<Integer>` dynamically
2. Compare performance: direct lambda vs MethodHandle vs reflection

---

## 3. Custom Bootstrap Method (Advanced)

**Goal**: Implement custom `invokedynamic` bootstrap.

```java
public class MyBootstrap {
    public static CallSite bootstrap(MethodHandles.Lookup caller,
                                     String name, MethodType type) {
        // Custom logic: e.g., return constant, lookup from registry, etc.
        MethodHandle target = MethodHandles.constant(String.class, "dynamic!");
        return new ConstantCallSite(MethodHandles.convertArguments(
            MethodHandles.constant(String.class, "hello"), type));
    }
}

// In bytecode (via ASM):
// invokedynamic "myMethod":(I)Ljava/lang/String; 
//   BootstrapMethods:
//     #0 MyBootstrap.bootstrap (I)Ljava/lang/String;
```

**Tasks**:
1. Write a bootstrap that returns a random number as String
2. Create a class with `invokedynamic` using ASM
3. Verify it works at runtime