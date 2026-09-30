# EXERCISES: Java in Kubernetes & Containers
## Lab 07 | Production Engineering Academy

---

## Exercise 1: Build a Hardened Distroless Image with Class Data Sharing (CDS)

### Objective
Create an optimized container image for a Spring Boot application that starts up 40% faster and runs securely as non-root.

### Tasks
1. Write a multi-stage Dockerfile using `eclipse-temurin:21-jdk` for builder and `eclipse-temurin:21-jre` for runtime.
2. Use Spring Boot layertools to split the fat JAR into 4 distinct layers:
   - `dependencies`
   - `spring-boot-loader`
   - `snapshot-dependencies`
   - `application`
3. Generate a CDS archive (`app-cds.jsa`) during the Docker build stage.
4. Add non-root user `appuser` (UID 10001) and enforce read-only root filesystem with a mounted `/dumps` volume.
5. Measure container startup time with CDS enabled vs disabled.

---

## Exercise 2: Simulate and Eliminate Rolling Update 502 Errors

### Objective
Demonstrate zero-downtime rolling deployment in Kubernetes using preStop hooks and graceful shutdown.

### Tasks
1. Deploy a sample Spring Boot service to Minikube or Kind cluster with 3 replicas.
2. Run continuous load test generating 100 req/s using `wrk` or `hey`:
   ```bash
   hey -z 60s -c 20 -q 5 http://<service-ip>/api/orders
   ```
3. During the test, trigger a rolling restart without `preStop` hook:
   ```bash
   kubectl rollout restart deployment/order-service
   ```
4. Observe HTTP 502 Bad Gateway responses in `hey` report.
5. Add `lifecycle.preStop.exec.command: ["/bin/sh", "-c", "sleep 15"]` and `server.shutdown: graceful`.
6. Trigger rolling restart again; observe 100% HTTP 200 OK responses with 0 failed requests.
