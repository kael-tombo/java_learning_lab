# Performance

## Performance Characteristics

### Memory Usage

| Pattern | Memory Cost |
|---------|-------------|
| Direct implementation | Minimal overhead |
| Wrapper/decorator | One extra object per wrapper |
| Proxy | One proxy object |
| Observer | Registration list grows with listeners |

### CPU Overhead

| Operation | Relative Cost |
|-----------|--------------|
| Direct method call | 1x baseline |
| Interface dispatch | 1-2x |
| Lambda/invokedynamic | 1-2x after warmup |
| Reflection | 10-100x |
| Dynamic proxy | 3-10x |

## Optimization Strategies

### 1. Profile First

Never optimize without profiling. Use JMH for microbenchmarks, JFR for production profiling, async-profiler for CPU sampling.

### 2. Optimize Hot Paths

Focus on code that executes frequently. Avoid object allocation in hot paths. Use primitive collections where possible.

### 3. Reduce Allocation

- Use object pools for expensive objects
- Avoid boxing in hot paths
- Pre-size collections when size is known
- Use StringBuilder instead of string concatenation in loops

### 4. Minimize Locking

- Use StampedLock for read-heavy workloads
- Prefer ConcurrentHashMap over synchronized maps
- Use Atomic classes for simple counters

## Performance Checklist

- Have you profiled before optimizing?
- Are collections pre-sized?
- Are there allocations in hot paths?
- Is locking minimized?
- Are you using appropriate data structures?
- Is the JVM warmed up before measuring?
