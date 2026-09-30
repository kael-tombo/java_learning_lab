# ANTI-PATTERNS: Java in Containers & Kubernetes
## Lab 07 | Production Engineering Academy

---

## Anti-Pattern 1: Hardcoding `-Xms` and `-Xmx` in Dockerfile

### The Mistake
Writing in `Dockerfile`:
`ENTRYPOINT ["java", "-Xmx4g", "-jar", "app.jar"]`

### Why It Fails
When Kubernetes resource requests/limits are changed in Helm charts or deployment manifests (e.g. downscaled to 2Gi in dev, or upscaled to 8Gi in production), the Docker container ignores Kubernetes configuration! It will either crash with OOMKill in dev or waste 50% of allocated RAM in production.

### The Correct Production Fix
Use dynamic percentage flags:
`-XX:InitialRAMPercentage=70.0 -XX:MaxRAMPercentage=70.0`
The JVM automatically adapts to whatever cgroup memory limit is configured by Kubernetes.

---

## Anti-Pattern 2: Missing `exec` in Shell Entrypoints (The PID 1 Signal Trap)

### The Mistake
In entrypoint script:
```bash
#!/bin/sh
java -jar app.jar
```
Or in Dockerfile:
`ENTRYPOINT ["sh", "-c", "java -jar app.jar"]` (without `exec`).

### Why It Fails
- `sh` runs as PID 1 inside the container.
- `java` runs as a child process (PID 7).
- When Kubernetes sends `SIGTERM` to terminate the pod, standard `sh` does NOT forward POSIX signals to child processes!
- The Java process never receives `SIGTERM`. It continues running until Kubernetes reaches `terminationGracePeriodSeconds` (default 30s) and brutally sends `SIGKILL` (Exit Code 137).
- Graceful shutdown logic, flushing in-flight orders, closing database connections, and committing Kafka offsets never execute!

### The Correct Production Fix
Always prefix with `exec` so Java replaces the shell and becomes PID 1:
`ENTRYPOINT ["sh", "-c", "exec java -jar app.jar"]`
Or use the JSON array exec form:
`ENTRYPOINT ["java", "-jar", "app.jar"]`
