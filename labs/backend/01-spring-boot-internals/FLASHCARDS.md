# Flashcards: Spring Boot Internals

## Q: What three annotations compose `@SpringBootApplication`?
**A:** `@Configuration` + `@EnableAutoConfiguration` + `@ComponentScan`

## Q: How is auto-configuration triggered?
**A:** By classes present on the classpath, evaluated via `@Conditional*` annotations.

## Q: Which file registers auto-configurations in Boot 3?
**A:** `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`

## Q: How do you change the embedded server port?
**A:** Set `server.port=8081` in `application.properties`/`application.yml`.

## Q: What is a Spring Boot starter?
**A:** A curated dependency set for one feature (e.g. `spring-boot-starter-web`).

## Q: How do you exclude an auto-configuration?
**A:** `@SpringBootApplication(exclude = DataSourceAutoConfiguration.class)`

## Q: How do you debug which auto-configurations applied?
**A:** Set `debug=true` or call `GET /actuator/conditions`.

## Q: `@Value` vs `@ConfigurationProperties`?
**A:** `@Value` = single value injection; `@ConfigurationProperties` = structured, validated, relaxed binding of a property group.

## Q: How do you run a Boot app from the CLI?
**A:** `mvn spring-boot:run` or `java -jar app.jar`

## Q: How do you add a custom health check?
**A:** Implement the `HealthIndicator` interface; it is picked up by `/actuator/health`.
