# Quiz: Spring Boot Internals

## Q1
Which annotation enables auto-configuration search on the classpath?
a) `@ComponentScan` b) `@EnableAutoConfiguration` c) `@SpringBootApplication` alone without imports d) `@ImportAutoConfiguration` only in tests
**Answer: b) `@EnableAutoConfiguration` (usually composed inside `@SpringBootApplication`)**

## Q2
Where are auto-configuration classes registered in Spring Boot 3?
a) `META-INF/spring.factories` b) `META-INF/spring/...AutoConfiguration.imports` c) `application.yml` d) `bootstrap.yml`
**Answer: b) `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`**

## Q3
What does `@ConditionalOnMissingBean` do?
a) Fails startup if the bean exists b) Creates the bean only if no bean of that type exists c) Deletes the bean d) Lazily proxies the bean
**Answer: b)**

## Q4
How do you see which auto-configurations were applied and which were skipped?
a) `debug=true` or the `/actuator/conditions` endpoint b) `info=true` c) Deleting `target/` d) `spring.main.banner-mode=off`
**Answer: a)**

## Q5
What is the role of a Spring Boot starter (e.g. `spring-boot-starter-web`)?
a) A JVM agent b) A curated dependency set plus default auto-configuration for a feature c) A code generator d) A Docker image
**Answer: b)**

## Q6
How do you exclude a specific auto-configuration?
a) `@SpringBootApplication(exclude = DataSourceAutoConfiguration.class)` b) Delete the jar c) `@Profile("!prod")` d) `spring.exclude=all`
**Answer: a)**

## Q7
What is the difference between `@Value` and `@ConfigurationProperties`?
a) No difference b) `@Value` injects single values; `@ConfigurationProperties` binds structured groups with validation and relaxed binding c) `@Value` is type-safe d) `@ConfigurationProperties` only works for Strings
**Answer: b)**

## Q8
When does a `@ConditionalOnClass(SomeClass.class)` auto-configuration back off?
a) When the class is present b) When the class is absent from the classpath c) On Fridays d) When the profile is `dev`
**Answer: b)**

## Q9
What does `spring-boot-starter-parent` provide?
a) Nothing b) Dependency management, default plugin config, and property defaults c) A database d) A web server binary
**Answer: b)**

## Q10
Which actuator endpoint reports application health?
a) `/actuator/beans` b) `/actuator/health` c) `/actuator/mappings` d) `/actuator/heapdump`
**Answer: b)**
