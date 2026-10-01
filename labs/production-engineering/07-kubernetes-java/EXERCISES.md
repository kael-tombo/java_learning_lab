# EXERCISES: Kubernetes & Containerized Java Engineering
## Lab 07 | Production Engineering Academy — Top 0.0001% Engineering

---

## Exercise 1: Reproducing and Eliminating Container Exit Code 137 (Linux OOM-Killer)

### 1. Objective
Reproduce the exact mechanism where a Java application whose heap fits within container limits is terminated with `Exit Code 137` by the Linux kernel due to non-heap memory expansion, and eliminate it using dynamic container ergonomics.

### 2. Implementation Tasks
1. Write a Java program `NonHeapMemoryLeaker.java`:
   - Allocates a small 1 GiB heap (`-Xms1g -Xmx1g`).
   - In a loop, allocates off-heap direct byte buffers using `ByteBuffer.allocateDirect(10 * 1024 * 1024)` without releasing them.
2. Package the application into a Docker container and set a strict memory limit of 1.5 GiB:
   ```bash
   docker run --rm -m 1536m -e JAVA_OPTS="-Xms1g -Xmx1g" my-app
   ```
3. Observe the crash:
   - Verify container exits with **code 137**.
   - Check `dmesg -T | grep -i oom-killer` to verify the Linux kernel issued `SIGKILL`.
   - Verify that **zero** `OutOfMemoryError` was logged in the console.
4. Refactor using dynamic percentage-based container sizing:
   ```bash
   docker run --rm -m 1536m \
     -e JAVA_TOOL_OPTIONS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=60.0 -XX:MaxDirectMemorySize=400m" \
     my-app
   ```
5. Observe that when direct memory expands, the JVM throws an explicit in-JVM `java.lang.OutOfMemoryError: Direct buffer memory` with a full actionable stack trace rather than crashing via a kernel SIGKILL.

---

## Exercise 2: Simulating and Eliminating Rolling Deployment 502 Errors

### 1. Objective
Simulate a rolling deployment under high-concurrency traffic in Kubernetes, measure the baseline rate of HTTP 502 Bad Gateway responses, and eliminate them completely using PreStop sleep hooks and Spring Boot graceful shutdown.

### 2. Implementation Tasks
1. Deploy a sample Spring Boot REST service to a local Kubernetes cluster (Minikube / k3d / kind) with 4 replicas behind an NGINX Ingress Controller.
2. In deployment manifest v1, omit `preStop` and omit `server.shutdown: graceful`.
3. Launch a load generator firing 1,000 requests/sec with continuous error logging:
   ```bash
   hey -z 60s -q 250 -c 50 http://sample-service.local/api/orders
   ```
4. While the load test is running, trigger a rolling update:
   ```bash
   kubectl set image deployment/sample-service app=sample-service:v2
   ```
5. Record the number of `502 Bad Gateway` and `Connection Refused` errors logged by `hey`.
6. Update deployment manifest v2:
   - Add `lifecycle.preStop.exec.command: ["/bin/sh", "-c", "sleep 15"]`.
   - Set `terminationGracePeriodSeconds: 60`.
   - Set `server.shutdown: graceful` and `spring.lifecycle.timeout-per-shutdown-phase: 30s`.
7. Re-run the test during another rolling update:
   - Verify that non-200 responses drop to **strictly zero (100% availability)**.

---

## Exercise 3: Breaking the Coupled Liveness Probe Death Spiral

### 1. Objective
Simulate a transient database interruption and observe how coupling the liveness probe to database connectivity causes a cascading cluster reboot, then remediate it by implementing decoupled liveness and readiness probes.

### 2. Implementation Tasks
1. Deploy PostgreSQL and a 10-replica Java service in Kubernetes.
2. Configure v1 with an anti-pattern liveness probe pointing to the aggregate `/actuator/health` endpoint:
   ```yaml
   livenessProbe:
     httpGet:
       path: /actuator/health
       port: 8080
     periodSeconds: 3
     failureThreshold: 2
   ```
3. Simulate a 10-second database failover by pausing the PostgreSQL container:
   ```bash
   docker pause $(docker ps -q -f name=postgres)
   sleep 10
   docker unpause $(docker ps -q -f name=postgres)
   ```
4. Monitor pod statuses with `kubectl get pods -w`:
   - Observe that all 10 pods enter `CrashLoopBackOff` simultaneously.
   - Note the connection storm hitting PostgreSQL when the database resumes.
5. Re-architect the probes:
   - Point `livenessProbe` strictly to `/actuator/health/liveness`.
   - Point `readinessProbe` to `/actuator/health/readiness`.
6. Re-run the 10-second database pause:
   - Verify that pods transition to `READY: 0/1` during the pause, but **zero containers are restarted**.
   - Verify that as soon as PostgreSQL resumes, pods automatically return to `READY: 1/1` within 5 seconds without restarting.

---

## Exercise 4: Cold Start Acceleration: JIT vs. AppCDS vs. Project CRaC

### 1. Objective
Benchmark and compare the cold-start latency of a Spring Boot 3.x microservice across standard JIT, Application Class Data Sharing (AppCDS), and Project CRaC.

### 2. Implementation Tasks
1. Measure standard JIT cold start:
   ```bash
   time java -jar app.jar
   # Check logged startup time: "Started Application in 18.42 seconds"
   ```
2. Generate AppCDS archive:
   ```bash
   # Step A: Generate classlist
   java -XX:ArchiveClassesAtExit=appcds.jsa -Dspring.context.exit=onRefresh -jar app.jar
   # Step B: Run with AppCDS archive
   time java -XX:SharedArchiveFile=appcds.jsa -jar app.jar
   # Verify startup time dropped by ~40% (e.g. down to 7.8 seconds)
   ```
3. Project CRaC Checkpoint & Restore (on an Ubuntu Linux host or container with CRIU):
   ```bash
   # Step A: Start JVM with CRaC checkpoint directory
   java -XX:CRaCCheckpointTo=/opt/crac-checkpoint -jar app.jar &
   PID=$!
   # Wait for full startup and warmup...
   sleep 20
   # Step B: Take snapshot
   jcmd $PID JDK.checkpoint
   # Step C: Restore from checkpoint
   time java -XX:CRaCRestoreFrom=/opt/crac-checkpoint
   ```
4. Record the final restore time from the console:
   - Verify the application is fully running and serving requests in **$< 40\text{ milliseconds}$**!
