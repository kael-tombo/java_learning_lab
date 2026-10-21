# Mathematical Foundation: GraalVM Native

## Startup Time Comparison
JVM startup = JVM_init + class_loading + bytecode_verification + JIT_warmup
Native startup = binary_load + initialization (typically 0.05-0.3s)

## Memory Comparison
JVM RSS = JVM_base (200MB) + heap + metaspace + code_cache + thread_stacks
Native RSS = executable_size (20MB) + heap + GC_overhead

## Build Time
Native image build time scales with code complexity:
- Simple app: 1-2 minutes
- Medium app: 3-5 minutes
- Complex app: 5-15 minutes

## Peak Throughput Ratio
Native/JVM peak ratio improves with:
- Less dynamic dispatch
- More inlining opportunities
- Better profile-guided optimization
Typically 80-95% of JVM peak, approaching parity with PGO.
