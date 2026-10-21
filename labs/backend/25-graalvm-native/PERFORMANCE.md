# Performance: GraalVM Native

| Metric | JVM (HotSpot) | Native Image | Improvement |
|--------|---------------|--------------|-------------|
| Startup time | 3-10s | 0.05-0.3s | 10-50x |
| Memory (RSS) | 200-500MB | 30-80MB | 3-6x |
| Image size | ~200MB (JRE) | 20-50MB | 4-10x |
| Peak throughput | 100% | 80-95% | -5 to -20% |
| Warmup time | seconds-minutes | instant | ~0 |

Note: Peak throughput is typically 80-95% of JVM after JIT warmup.
