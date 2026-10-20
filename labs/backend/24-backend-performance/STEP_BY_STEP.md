# Step by Step: Performance Tuning

## JMH Benchmark
`java
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.MICROSECONDS)
@State(Scope.Thread)
public class StringBenchmark {
    private final String STRING = "Hello, World!";

    @Benchmark
    public String stringConcat() {
        return STRING + " " + System.currentTimeMillis();
    }

    @Benchmark
    public String stringBuilder() {
        return new StringBuilder(STRING)
            .append(" ")
            .append(System.currentTimeMillis())
            .toString();
    }
}
`

## HikariCP Configuration
`yaml
spring:
  datasource:
    hikari:
      maximum-pool-size: 20
      minimum-idle: 5
      idle-timeout: 300000
      connection-timeout: 2000
      max-lifetime: 1800000
      leak-detection-threshold: 60000
`

## Caffeine Cache
`java
@Bean
public Cache<String, Product> productCache() {
    return Caffeine.newBuilder()
        .maximumSize(10_000)
        .expireAfterWrite(5, TimeUnit.MINUTES)
        .recordStats()
        .build();
}
`
"@

Write-Doc (Join-Path C:\Users\jratombo-adm\Desktop\java_learning_lab\labs\backend\24-backend-performance "CODE_DEEP_DIVE.md") @"
# Code Deep Dive: Performance

## HikariCP Internals
HikariCP uses:
- ConcurrentBag (lock-free collection) for connection management
- FastList (optimized ArrayList) for statement cleanup
- Hybrid approach for connection timeout (Spin-lock + wait/notify)
- Zero-overhead proxy (no reflection for JDBC calls)

## Caffeine Cache Internals
Caffeine uses:
- W-TinyLFU (Window Tiny Least Frequently Used) eviction policy
- Near-optimal hit rate with minimal overhead
- Asynchronous refresh with refreshAfterWrite
- Statistics tracking (hit rate, load time, eviction count)

## JIT Compilation
HotSpot JVM identifies hot methods and compiles them to native code:
- -XX:+PrintCompilation to see compilation
- Tiered compilation: interpreter → C1 → C2
- Inlining threshold: -XX:MaxInlineSize (default 35 bytes)
- On-stack replacement (OSR) for long-running loops
