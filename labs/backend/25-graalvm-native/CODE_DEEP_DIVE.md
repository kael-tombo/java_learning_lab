# Code Deep Dive: GraalVM Native Image

## Maven configuration

```xml
<plugin>
  <groupId>org.graalvm.buildtools</groupId>
  <artifactId>native-maven-plugin</artifactId>
  <version>0.10.3</version>
  <configuration>
    <mainClass>com.example.DemoApplication</mainClass>
    <buildArgs>--no-fallback -H:+ReportExceptionStackTraces</buildArgs>
  </configuration>
  <executions>
    <execution><goals><goal>process-aot</goal></goals></execution>
  </executions>
</plugin>
```

Run: `mvn -Pnative native:compile` (needs `GRAALVM_HOME` and the
`native-image` tool installed). `-Pnative` usually sets
`spring-boot-maven-plugin`'s `native-image` goal.

## Registering reflection hints

```java
@Component
public class Hints implements RuntimeHintsRegistrar {
    @Override
    public void registerHints(RuntimeHints hints, ClassLoader cl) {
        hints.reflection().registerType(Order.class, new MemberCategory[]{
            MemberCategory.INVOKE_DECLARED_CONSTRUCTORS,
            MemberCategory.INVOKE_DECLARED_METHODS});
        hints.resources().registerPattern("static/**");
        hints.proxies().registerJdkProxy(PaymentClient.class);
    }
}
```

Pitfall: forgetting the registrar compiles fine, ships a native binary, and
throws `ClassNotFoundException: Order` the first time Jackson touches it.
Alternative for a one-off: `@RegisterReflectionForBinding(Order.class)` on
the application class.

## Constructor binding (Jackson) — the safer path

```java
public record Order(Long id, int totalCents, String currency) {}
```

Records are fully supported by Jackson and GraalVM; no hints needed.

## HikariCP + Postgres in native

```properties
spring.datasource.url=jdbc:postgresql://db:5432/app
spring.datasource.driver-class-name=org.postgresql.Driver
```

Pitfall: a custom JDBC driver that loads native libraries without
`jni-config.json` — the error arrives at boot as `UnsatisfiedLinkError` ,
not at build time.

## Testing the native binary in CI

```yaml
- name: Build
  run: mvn -Pnative native:compile -DskipTests
- name: Smoke test
  run: |
    ./target/app &
    curl --retry 10 --retry-connrefused localhost:8080/actuator/health
    curl localhost:8080/orders | jq .
```

Pitfall: a green JVM `mvn test` tells you nothing about native correctness;
smoke-test the artifact itself.

## Tracer / fall-back mode for discovery

```bash
java -agentlib:native-image-agent=config-output-dir=src/main/resources/META-INF/native-image \
     -jar target/app.jar
# exercise every endpoint; commit the generated reflect-config/resource-config/proxy-config
```

Useful, but the recommended path is replacing this with
`RuntimeHintsRegistrar` — generated JSON drifts out of version control.

## Memory sizing

```bash
./target/app -Xmx256m -XX:MaxRAMPercentage=75.0
```

Native images don't grow the heap like HotSpot ergonomics assume; set
explicit limits in containers.
