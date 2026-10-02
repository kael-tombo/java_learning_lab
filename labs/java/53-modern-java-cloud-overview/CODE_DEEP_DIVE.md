# CODE_DEEP_DIVE — Cloud-native Java skeleton

Reference layout (adapt per framework; Spring Boot shown):

## 1. `Dockerfile` (layered, non-root, cgroup-aware)

```dockerfile
FROM eclipse-temurin:21-jre-jammy AS layers
WORKDIR /app
COPY target/*.jar app.jar
RUN java -Djarmode=layertools -jar app.jar extract

FROM eclipse-temurin:21-jre-jammy
RUN addgroup --system app && adduser --system --ingroup app appuser
USER appuser
WORKDIR /app
COPY --from=layers app/dependencies/ ./
COPY --from=layers app/spring-boot-loader/ ./
COPY --from=layers app/snapshot-dependencies/ ./
COPY --from=layers app/application/ ./
ENV JAVA_OPTS="-XX:MaxRAMPercentage=75.0 -XX:+UseG1GC"
ENTRYPOINT ["sh","-c","java $JAVA_OPTS org.springframework.boot.loader.launch.JarLauncher"]
```

Layers: dependency/app split → rebuilds ship app layer only. `USER`
non-root. No `-Xmx` — `MaxRAMPercentage` tracks the cgroup limit.

## 2. `application.yml` (12-factor: env wins)

```yaml
server:
  port: ${PORT:8080}
spring:
  datasource:
    url: ${DB_URL}
    username: ${DB_USER}
    password: ${DB_PASSWORD}   # from secret manager, never baked in
management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus
  endpoint:
    health:
      probes:
        enabled: true          # /liveness + /readiness for orchestrators
```

## 3. Health + tracing hooks (Java)

```java
// Readiness already covers DB via spring-boot-starter-actuator;
// add OpenTelemetry starter for W3C trace propagation:
// implementation 'io.micrometer:micrometer-tracing-bridge-otel'
```

Probes gate rolling deploys (labs 54–56 wire them to ALB/GCLB/App Gateway
health checks); traces flow to X-Ray / Cloud Trace / App Insights with
zero code changes beyond the starter + endpoint config.
