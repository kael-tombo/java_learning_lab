# Internals: GraalVM Native

## Points-to Analysis
GraalVM's static analysis traces all reachable code starting from the entry point (main method). It:
1. Builds a call graph
2. Determines which types are instantiated
3. Determines which methods are called
4. Determines which fields are accessed
5. Detects reflection usage and includes declared classes

## SubstrateVM GC
SubstrateVM uses a serial GC by default (single-threaded, stop-the-world). For larger heaps, G1-like collectors are available as experimental.
