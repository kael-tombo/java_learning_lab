# Code Deep Dive: Performance Tuning

## HikariCP sizing

```properties
spring.datasource.hikari.maximum-pool-size=20     # match DB; not "more is better"
spring.datasource.hikari.minimum-idle=5
spring.datasource.hikari.connection-timeout=3000
spring.datasource.hikari.max-lifetime=1700000     # below DB wait_timeout
spring.datasource.hikari.idle-timeout=600000
```

Pitfall: the default 10 with a Tomcat pool of 200 silently serializes; a
500-connection pool against a 100-connection Postgres fails every other
client. Use `connection-timeout` close to your request SLA and monitor the
`hikaricp.connections.pending` metric.

## N+1 fix with entity graph

```java
@EntityGraph(attributePaths = {"author", "tags"})
@Query("select b from Book b where b.publishedAt > :since")
List<Book> recent(@Param("since") Instant since);
```

Or a join fetch:

```java
@Query("select b from Book b join fetch b.author where b.id in :ids")
```

Pitfall: `join fetch` on a `@OneToMany` collection multiplies rows (Cartesian
product with every other collection fetched in the same query); fetch one
collection at a time.

## Caffeine cache with jitter + single flight

```java
Cache<String, Product> products = Caffeine.newBuilder()
    .maximumSize(10_000)
    .expireAfterWrite(Duration.ofMinutes(5).plusMillis(random.nextInt(30_000)))
    .recordStats()
    .build();

Product get(String id) {
    return products.get(id, repo::findById);   // single-flight: concurrent misses coalesce
}
```

Pitfall: uniform TTLs stampede exactly when the key is hot; add jitter.

## Bounded async with backpressure

```java
@Bean
ExecutorService remoteCalls() {
    // bounded queue + caller-runs is explicit backpressure
    return new ThreadPoolExecutor(16, 32, 60, SECONDS,
        new ArrayBlockingQueue<>(200),
        new ThreadPoolExecutor.CallerRunsPolicy());
}
```

## Tomcat thread pool alignment

```properties
server.tomcat.threads.max=64          # not 200
server.tomcat.threads.min-spare=10
spring.datasource.hikari.maximum-pool-size=32
```

## GC-friendly hot loop

```java
// avoid: boxed Long, streams per row
long total = 0;
for (var row : rows) total += row.getAmountCents();   // primitive accumulation
```

## Profile with async-profiler

```bash
java -agentpath:libasyncProfiler.so=start,event=cpu,file=flame.html -jar app.jar
```

Look for unexpected `Thread.sleep`, monitor waits, and Jackson serialization
frames at the top of the flamegraph before touching JVM flags.

## JMH skeleton

```java
@BenchmarkMode(Mode.AverageTime)
@OutputTimeUnit(TimeUnit.MICROSECONDS)
@Warmup(iterations = 3)
@Measurement(iterations = 5)
public class JsonBench {
    @Benchmark
    public String roundTrip(Blackhole bh, State s) throws Exception {
        bh.consume(objectMapper.readValue(s.json, Order.class));
        return "ok";
    }

    @State(Scope.Thread)
    public static class State {
        final String json = "{\"id\":1,\"amount\":100}";
        final ObjectMapper objectMapper = new ObjectMapper();
    }
}
```

Pitfall: constant-folding — always consume results via `Blackhole`, or JMH
dead-code-eliminates the benchmark into a 0.0x report.
