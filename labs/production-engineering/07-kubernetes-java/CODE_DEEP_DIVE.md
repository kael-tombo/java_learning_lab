# CODE DEEP DIVE: Production Kubernetes Java Configuration
## Lab 07 | Production Engineering Academy

---

## Pattern 1: Production Multi-Stage Dockerfile for High-Performance Java

```dockerfile
# Stage 1: Build & Class Data Sharing (CDS) generation
FROM eclipse-temurin:21-jdk-jammy AS builder
WORKDIR /workspace

# Copy Maven wrapper and POM to cache dependencies
COPY pom.xml mvnw ./
COPY .mvn .mvn
RUN ./mvnw dependency:go-offline -B

# Build application JAR
COPY src src
RUN ./mvnw package -DskipTests -B

# Extract Spring Boot layers for optimal Docker layer caching
WORKDIR /workspace/extracted
RUN java -Djarmode=layertools -jar /workspace/target/*.jar extract

# Perform CDS Training Run to accelerate JVM container cold-start by 40%
RUN java -XX:ArchiveClassesAtExit=app-cds.jsa \
         -Dspring.context.exit=onRefresh \
         -jar /workspace/target/*.jar || true

# Stage 2: Minimal Distroless / Hardened Runtime
FROM eclipse-temurin:21-jre-jammy
WORKDIR /application

# Run as non-root user (Security Best Practice)
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash appuser && \
    mkdir -p /dumps /application && \
    chown -R appuser:appgroup /dumps /application

USER 10001:10001

# Copy layers separately to maximize docker layer reuse across builds
COPY --chown=10001:10001 --from=builder /workspace/extracted/dependencies/ ./
COPY --chown=10001:10001 --from=builder /workspace/extracted/spring-boot-loader/ ./
COPY --chown=10001:10001 --from=builder /workspace/extracted/snapshot-dependencies/ ./
COPY --chown=10001:10001 --from=builder /workspace/extracted/application/ ./

ENV JAVA_OPTS="\
-XX:+UseContainerSupport \
-XX:MaxRAMPercentage=70.0 \
-XX:InitialRAMPercentage=70.0 \
-XX:+UseZGC \
-XX:+ZGenerational \
-XX:+HeapDumpOnOutOfMemoryError \
-XX:HeapDumpPath=/dumps/heap.hprof \
-XX:+ExitOnOutOfMemoryError \
-Djava.security.egd=file:/dev/./urandom \
-Dsun.net.inetaddr.ttl=10"

EXPOSE 8080 8081
ENTRYPOINT ["sh", "-c", "exec java $JAVA_OPTS org.springframework.boot.loader.launch.JarLauncher"]
```

---

## Pattern 2: Complete Production Kubernetes Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: payment-service
  labels:
    app: payment-service
spec:
  replicas: 6
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 0
  selector:
    matchLabels:
      app: payment-service
  template:
    metadata:
      labels:
        app: payment-service
    spec:
      terminationGracePeriodSeconds: 60
      # Anti-affinity to ensure pods are scheduled across distinct AZs and physical nodes
      topologySpreadConstraints:
        - maxSkew: 1
          topologyKey: topology.kubernetes.io/zone
          whenUnsatisfiable: DoNotSchedule
          labelSelector:
            matchLabels:
              app: payment-service
      containers:
        - name: payment-service
          image: 123456789.dkr.ecr.us-east-1.amazonaws.com/payment-service:v2.4.1
          imagePullPolicy: IfNotPresent
          resources:
            requests:
              cpu: "2000m"
              memory: "4Gi"
            limits:
              # In latency-critical JVM workloads, CPU limit is either omitted or set high to prevent CFS throttling
              memory: "4Gi"
          lifecycle:
            preStop:
              exec:
                command: ["/bin/sh", "-c", "sleep 15"]
          startupProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8081
            failureThreshold: 30
            periodSeconds: 3
          livenessProbe:
            httpGet:
              path: /actuator/health/liveness
              port: 8081
            periodSeconds: 10
            failureThreshold: 3
          readinessProbe:
            httpGet:
              path: /actuator/health/readiness
              port: 8081
            periodSeconds: 5
            failureThreshold: 2
          volumeMounts:
            - name: heap-dumps
              mountPath: /dumps
      volumes:
        - name: heap-dumps
          emptyDir:
            sizeLimit: 8Gi
```
