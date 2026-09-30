# CODE DEEP DIVE: Cost Engineering & FinOps Patterns
## Lab 16 | Production Engineering Academy

---

## Pattern 1: Kubernetes Topology Aware Routing Manifest

```yaml
apiVersion: v1
kind: Service
metadata:
  name: payment-service
  labels:
    app: payment-service
  annotations:
    # Routes client requests to endpoints in the same AZ to eliminate cross-AZ transfer costs ($0.02/GB)
    service.kubernetes.io/topology-mode: Auto
spec:
  type: ClusterIP
  ports:
    - name: grpc
      port: 50051
      targetPort: 50051
  selector:
    app: payment-service
```

---

## Pattern 2: JVM Memory Sizing & Periodic Uncommit Script

```bash
#!/usr/bin/env bash
# Cost-optimized JVM startup script for ARM64 Graviton / Containerized workloads

# 1. Right-sized percentage memory allocation
# Leaves 25% for Metaspace, Thread stacks, and OS page cache
JAVA_OPTS="-XX:+UseContainerSupport -XX:MaxRAMPercentage=75.0"

# 2. Generational ZGC with active memory uncommit (returns unused RAM back to Linux kernel)
JAVA_OPTS="${JAVA_OPTS} -XX:+UseZGC -XX:+ZGenerational"
JAVA_OPTS="${JAVA_OPTS} -XX:+ZUncommit -XX:ZUncommitDelay=300" # Returns unused heap pages after 5m idle

# 3. Compressed OOPs and Class Pointers (keeps object references to 32-bit under 32GB heap)
JAVA_OPTS="${JAVA_OPTS} -XX:+UseCompressedOops -XX:+UseCompressedClassPointers"

# 4. Strip debug symbols from production container runtime image to save storage transfer cost
exec java ${JAVA_OPTS} -jar /application/app.jar
```
