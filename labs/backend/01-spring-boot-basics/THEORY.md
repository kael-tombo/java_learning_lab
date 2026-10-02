# Theory: Spring Boot Basics

## Core Concepts

### Auto-Configuration
Spring Boot's auto-configuration attempts to automatically configure your Spring application based on the jar dependencies you have added. It is implemented via `@EnableAutoConfiguration` and `spring.factories` files.

```java
// Spring Boot checks for classes on the classpath
@ConditionalOnClass(DataSource.class)
@ConditionalOnMissingBean(DataSource.class)
@ConditionalOnProperty(name = "spring.datasource.url")
public DataSource dataSource() {
    return DataSourceBuilder.create().build();
}
```

### Conditionals Used
- `@ConditionalOnClass` / `@ConditionalOnMissingClass`
- `@ConditionalOnBean` / `@ConditionalOnMissingBean`
- `@ConditionalOnProperty`
- `@ConditionalOnResource`
- `@ConditionalOnWebApplication`

### Starters
Starters are convenient dependency descriptors. `spring-boot-starter-web` includes Tomcat, Spring MVC, and Jackson.

### Property Binding
Type-safe configuration via `@ConfigurationProperties`:

```java
@ConfigurationProperties(prefix = "app.datasource")
public class DataSourceProperties {
    private String url;
    private String username;
    private String password;
}
```

## Sourced field notes (fetched Oct 2026 — verify before citing)
- "Building a RESTful Web Service" (Spring Guides, living guide — accessed Oct 2026) — https://spring.io/guides/gs/rest-service/ — Takeaway tied to lab controller exercise: use `@RestController` + `@GetMapping("/greeting")` + `@RequestParam(defaultValue="World")` pattern from the guide when building the lab's first endpoint; verify `AtomicLong` counter behavior across repeated GETs.
- "Building a RESTful Web Service" (Spring Guides, living guide — accessed Oct 2026) — https://spring.io/guides/gs/rest-service/ — Takeaway tied to lab serialization config: the guide relies on `spring-boot-starter-web` pulling in Jackson so a `record Greeting(long id, String content)` marshals to JSON with zero manual converter code; confirm Jackson is on the classpath before debugging empty responses.
- "Building a RESTful Web Service" (Spring Guides, living guide — accessed Oct 2026) — https://spring.io/guides/gs/rest-service/ — Takeaway tied to lab auto-configuration exercise: `@SpringBootApplication` = `@Configuration` + `@EnableAutoConfiguration` + `@ComponentScan`, which is why `spring-webmvc` on the classpath auto-registers `DispatcherServlet` and picks up controllers under `com/example`.
- "Building a RESTful Web Service" (Spring Guides, living guide — accessed Oct 2026) — https://spring.io/guides/gs/rest-service/ — Takeaway tied to lab build/run configs: run via `./gradlew bootRun` or `./mvnw spring-boot:run`, ship via `./gradlew build` / `./mvnw clean package` then `java -jar <artifact>.jar`; compare lab startup logs against the guide's expected few-seconds boot.
