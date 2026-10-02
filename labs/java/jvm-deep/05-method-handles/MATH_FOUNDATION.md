# MATH_FOUNDATION — Method Handles & invokedynamic

## 1. Method Handle Performance

### Call Site Mechanics

```
invokedynamic site → BootstrapMethod → CallSite → Target MethodHandle
```

**Cost breakdown**:
| Operation | Cost |
|-----------|------|
| Bootstrap (first call) | ~100-500μs |
| CallSite.getTarget() | ~1-5ns (JIT) |
| MethodHandle.invokeExact() | ~1-3ns (intrinsic) |
| MethodHandle.invoke() | ~5-10ns (boxing) |

### Invocation Overhead

| Call Type | Relative Cost |
|-----------|--------------|
| Direct call | 1x (baseline) |
| MethodHandle.invokeExact() | 1.0-1.5x |
| MethodHandle.invoke() | 2-5x (boxing) |
| Reflection | 10-50x |
| lambda (JDK 8+) | ~1x (intrinsic) |

---

## 1. Method Handle Invocation Overhead

### Direct vs Indirect Call Cost

| Call Type | Relative Cost | Notes |
|-----------|---------------|-------|
| Direct method call | 1.0x | JIT inlines |
| MethodHandle.invokeExact() | 1.0-1.5x | Intrinsic, often inlined |
| MethodHandle.invoke() | 2-5x | Boxing/unboxing |
| Reflection (Method.invoke) | 10-50x | No inlining, security checks |
| Reflection (setAccessible) | 5-20x | Still slow |

### Invocation Overhead Breakdown

```
MethodHandle.invokeExact():
  1. Type check (eliminated by JIT)
  2. Direct jump to target (inlined)
  
MethodHandle.invoke():
  1. Box primitives → Object[]
  2. Type check
  3. Invoke target
  3. Unbox result
```

---

## 2. invokedynamic Mechanics

### Bootstrap Method Cost

```
First call:  BootstrapMethod() → CallSite → cache
Subsequent:  CallSite.getTarget() → invokeExact() → target
```

| Phase | Cost | Notes |
|-------|------|-------|
| Bootstrap (first call) | ~100-500μs | Class loading, linkage |
| CallSite.getTarget() | ~1-5ns | Inlined by JIT |
| invokeExact() | ~1-3ns | Intrinsic |

### Call Site Types

| Type | Target Mutability | Use Case |
|--------|-------------------|----------|
| ConstantCallSite | Immutable | Lambdas, constants |
| VolatileCallSite | Volatile read | Hot-reload, config |
| MutableCallSite | Synchronized | Dynamic dispatch |

---

## 2. Method Handle Transformation Costs

### Transformation Overhead

| Operation | Cost | Notes |
|-----------|------|-------|
| `filterArguments` | ~5-10ns | Small adapter |
| `filterReturnValue` | ~5-10ns | Small adapter |
| `bindTo` | ~1ns | Field set |
| `asSpreader` | ~5-20ns | Array allocation |
| `asCollector` | ~5-20ns | Array allocation |
| `guardWithTest` | ~10-20ns | Branch + call |

### Transformation Composition

Chaining transformations adds overhead:
```
mh.filterArguments(f).filterReturnValue(g).bindTo(x)
```
Each layer: ~5-10ns overhead. Keep chains short in hot paths.

---

## 2. invokedynamic Bootstrap Cost

### First Call Overhead

```
invokedynamic #1:
  1. Resolve bootstrap method (class loading if needed)
  2. Execute bootstrap method
  2. Create CallSite (ConstantCallSite ~100ns)
  4. Cache in constant pool cache
  5. Invoke target
  
Total first call: ~100-500μs (cold) → ~1-5μs (warm classloader)
```

### Constant Pool Cache

JVM caches CallSite per `invokedynamic` instruction. Subsequent calls:
- Read from constant pool cache: ~1ns
- `CallSite.getTarget()` → inline target

---

## 3. Lambda vs MethodHandle Performance

### Lambda vs MethodHandle vs Anonymous Class

| Implementation | Throughput (ops/s) | Memory |
|----------------|-------------------|--------|
| Lambda (Java 8+) | 1.0x (baseline) | Low |
| MethodHandle.invokeExact | 0.95-1.0x | Low |
| Anonymous class | 0.8-1.0x | Medium (class load) |
| Reflection | 0.02-0.1x | High |

**Key insight**: Lambdas compile to `invokedynamic` + `LambdaMetafactory` → `ConstantCallSite` → direct MethodHandle. Performance ≈ direct call after JIT.

---

## 3. Lambda vs MethodHandle vs Reflection

### Performance Comparison

| Approach | Throughput | Memory | Use Case |
|----------|------------|--------|----------|
| Lambda (Java 8+) | 1.0x | Low | Preferred |
| MethodHandle.invokeExact | 0.95-1.0x | Low | Dynamic |
| Anonymous class | 0.8-1.0x | Medium | Legacy |
| Reflection (Method.invoke) | 0.02-0.1x | High | Dynamic/unknown |

### Lambda Compilation

```
Lambda → invokedynamic → LambdaMetafactory.metafactory
  → ConstantCallSite → MethodHandle → invokeExact
```

JIT inlines the entire chain → equivalent to direct call.

---

## 3. Lambda vs MethodHandle vs Reflection

### Throughput Comparison (normalized to lambda = 1.0)

| Implementation | Relative Throughput | Memory |
|----------------|--------------------|--------|
| Lambda (Java 8+) | 1.00x | Low |
| MethodHandle.invokeExact | 0.95-1.00x | Low |
| Anonymous inner class | 0.80-1.00x | Medium |
| Reflection (Method.invoke) | 0.02-0.10x | High |

**Why lambda wins**: `invokedynamic` → `LambdaMetafactory` → `ConstantCallSite` → direct MethodHandle → JIT inlines completely.

---

## 4. Bootstrap Method Cost

### First Call Overhead

```
invokedynamic #1:
  1. Resolve bootstrap method (class loading if needed)
  2. Execute bootstrap method
  3. Create CallSite (ConstantCallSite ~100ns)
  4. Cache in constant pool cache
  4. Invoke target

Total first call: ~100-500μs (cold) → ~1-5μs (warm classloader)
```

### Constant Pool Cache

JVM caches CallSite per `invokedynamic` instruction. Subsequent calls:
- Read from constant pool cache: ~1ns
- `CallSite.getTarget()` → inline target

---

## 4. Lambda vs MethodHandle Performance

### Benchmark Data (relative)

| Operation | Relative Throughput | Notes |
|-----------|---------------------|-------|
| Lambda (Java 8+) | 1.00x | Baseline |
| MethodHandle.invokeExact | 0.95-1.00x | Best for dynamic |
| Anonymous class | 0.80-1.00x | Class load overhead |
| Reflection (Method.invoke) | 0.02-0.10x | Slow |

**Why lambda wins**: `invokedynamic` → `LambdaMetafactory` → `ConstantCallSite` → direct MethodHandle → JIT inlines completely. Equivalent to direct call after warmup.