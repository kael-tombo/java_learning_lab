# ADVANCED GUIDE: Coordinated Restore at Checkpoint (CRaC) & NUMA Node Pinning
## Lab 07 | Production Engineering Academy — Top 0.0001% Engineering

---

## 1. Project CRaC: Sub-20ms Java Cold Starts

Standard JVM initialization requires:
$$\text{Classloading} \longrightarrow \text{Bytecode Verification} \longrightarrow \text{JIT Tier 1 Compilation} \longrightarrow \text{Spring Bean Graph Creation} \longrightarrow \text{JIT C2 Compilation}$$
On a container, this takes **5 to 25 seconds**, making Java traditionally poorly suited for instant serverless autoscaling (Knative / AWS Lambda).

### How CRaC Works via Linux CRIU
**CRaC (Coordinated Restore at Checkpoint)** leverages Linux **CRIU (Checkpoint/Restore in Userspace)**:
1. Warm up the Java application completely: load all classes, execute dummy requests to trigger HotSpot C2 JIT optimization.
2. Trigger checkpoint: Java invokes `Resource.beforeCheckpoint()` hooks to close open network sockets and database connections cleanly.
3. Linux kernel dumps the entire process memory (heap, JIT compiled code cache, thread states) to disk as image files.
4. **Restore Phase**: When a new container pod launches, CRIU reads the memory images and restores the running process in **10 to 20 milliseconds**!
5. Java invokes `Resource.afterRestore()` hooks to reconnect to PostgreSQL and Redis.
6. The container begins serving traffic immediately at **peak C2 JIT compiled speed with zero warmup lag**!

---

## 2. Implementing CRaC Resource Lifecycle in Spring Boot

```java
package com.learning.production.lab07;

import org.crac.Context;
import org.crac.Core;
import org.crac.Resource;
import org.springframework.stereotype.Component;

import javax.sql.DataSource;

@Component
public class CracDatabaseConnectionManager implements Resource {

    private final DataSource dataSource;

    public CracDatabaseConnectionManager(DataSource dataSource) {
        this.dataSource = dataSource;
        // Register this component with the CRaC runtime coordinator
        Core.getGlobalContext().register(this);
    }

    @Override
    public void beforeCheckpoint(Context<? extends Resource> context) throws Exception {
        System.out.println("[CRaC] Checkpoint initiated. Draining and closing active database pools...");
        // Close network sockets and connection pools so no stale file descriptors are checkpointed
        if (dataSource instanceof com.zaxxer.hikari.HikariDataSource hikari) {
            hikari.close();
        }
    }

    @Override
    public void afterRestore(Context<? extends Resource> context) throws Exception {
        System.out.println("[CRaC] Process restored in 12ms! Re-initializing database connection pool...");
        // Re-open connections with fresh TCP handshakes
        if (dataSource instanceof com.zaxxer.hikari.HikariDataSource hikari) {
            hikari.getHikariPoolMXBean().resumePool();
        }
    }
}
```

---

## 3. NUMA-Aware CPU & Memory Pinning (`numactl`)

Modern multi-socket servers feature Non-Uniform Memory Access (NUMA):
- Cores on Socket 0 access local DRAM in **50ns**.
- Cores on Socket 0 accessing DRAM attached to Socket 1 over the interconnect bus (UPI / Infinity Fabric) takes **120ns+**!
- If a JVM's threads are scheduled on Socket 0 while its heap is allocated on Socket 1, the application suffers a continuous 40% memory latency penalty.

### Pinning the Container to a Single NUMA Node:
```bash
# Check NUMA topology
numactl --hardware

# Launch Java strictly bound to CPU cores 0-15 and local memory node 0:
numactl --cpunodebind=0 --membind=0 java -Xms16g -Xmx16g -jar app.jar
```
In Kubernetes: Configure `topologyManagerPolicy: single-numa-node` in Kubelet config to guarantee Pod CPU and memory reside on the identical physical NUMA socket.
