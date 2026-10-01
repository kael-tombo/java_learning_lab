# Exercises: Spring Boot Internals

## Exercise 1: Inspect Auto-Configuration
Create a minimal Spring Boot app, set `debug=true`, and run it. From the
conditions report, list (a) two auto-configurations that applied and
(b) two that backed off, with the reason each backed off.

## Exercise 2: Conditional Bean
Write an auto-configuration that creates bean `ServiceA` only when
`feature.x.enabled=true`, and bean `ServiceB` only when `ServiceA` exists
AND class `com.fasterxml.jackson.databind.ObjectMapper` is on the classpath.

## Exercise 3: Custom Starter
Build a `greeting-starter` that auto-configures a `GreetingService` when
property `greeting.message` is set. Package it as a separate Maven module and
consume it from a demo app. Verify back-off when the property is absent.

## Exercise 4: Configuration Binding
Create a `@ConfigurationProperties(prefix = "mail")` class (host, port,
username, password) with JSR-303 validation. Demonstrate profile-specific
overrides via `application-dev.yml` and `application-prod.yml`.

## Exercise 5: Custom Actuator Endpoint
Add a custom actuator endpoint (`@Endpoint(id = "buildinfo")`) returning
version, build timestamp, and active profiles. Expose it and query it with curl.
