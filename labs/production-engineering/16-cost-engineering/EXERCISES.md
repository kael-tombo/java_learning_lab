# EXERCISES: Cloud Cost Engineering & FinOps for High-Scale Java
## Lab 16 | Production Engineering Academy — Top 0.0001% Engineering

---

## Exercise 1: Empirically Proving the 32 GB Compressed OOPs Capacity Cliff

### 1. Objective
Measure and prove that an application configured with `-Xmx32g` stores fewer domain objects before crashing with an `OutOfMemoryError` than the exact same application configured with `-Xmx31g`.

### 2. Implementation Tasks
1. Write a Java class `CompressedOopsCapacityTest`:
   ```java
   public class CompressedOopsCapacityTest {
       static class DomainRecord {
           Object f1, f2, f3, f4, f5, f6;
           long id;
           double value;
       }
       public static void main(String[] args) {
           List<DomainRecord> list = new ArrayList<>();
           long count = 0;
           try {
               while (true) {
                   DomainRecord r = new DomainRecord();
                   r.f1 = "k1"; r.f2 = "k2"; r.f3 = "k3";
                   r.f4 = "k4"; r.f5 = "k5"; r.f6 = "k6";
                   list.add(r);
                   count++;
               }
           } catch (OutOfMemoryError e) {
               System.err.println("ALLOCATED COUNT BEFORE OOM: " + count);
           }
       }
   }
   ```
2. Run with `-Xmx31g`:
   ```bash
   java -Xms31g -Xmx31g -XX:+UseG1GC CompressedOopsCapacityTest
   ```
3. Run with `-Xmx32g`:
   ```bash
   java -Xms32g -Xmx32g -XX:+UseG1GC CompressedOopsCapacityTest
   ```
4. Record the final object counts and inspect object layout using JOL:
   ```bash
   java -jar jol-cli.jar internals CompressedOopsCapacityTest\$DomainRecord
   ```

### 3. Expected Observations & Proof
- **With `-Xmx31g`**: JOL reports pointer references are **4 bytes**. Total objects allocated before OOM: $\approx 285{,}000{,}000$.
- **With `-Xmx32g`**: JOL reports pointer references are **8 bytes**. Total objects allocated before OOM: $\approx 220{,}000{,}000$.
- **Conclusion**: Increasing the heap by 1 GB reduced effective data capacity by **over 65 million objects ($22.8\%$ capacity loss)** due to pointer expansion!

---

## Exercise 2: Simulating Cross-AZ Egress Reduction via Topology-Aware Routing

### 1. Objective
Implement and verify a Kubernetes cluster configuration that restricts microservice communication to the same Availability Zone, eliminating $85\%+$ of cross-AZ egress charges.

### 2. Implementation Tasks
1. Create a 3-AZ test cluster (e.g. using `k3d` or `kind` with zone labels: `topology.kubernetes.io/zone=us-east-1a`, `us-east-1b`, `us-east-1c`).
2. Deploy a backend service with 6 replicas and `topologySpreadConstraints` enforcing equal distribution (2 pods per zone).
3. Annotate the Service with `service.kubernetes.io/topology-mode: Auto`.
4. Inspect the generated `EndpointSlice` resources:
   ```bash
   kubectl get endpointslice -l kubernetes.io/service-name=backend-service -o yaml
   ```
   Verify that endpoints contain `hints.forZones` assigned to their respective local zone.
5. Deploy a client pod pinned to `us-east-1a` that fires 10,000 HTTP requests to the backend service.
6. Check access logs on all 6 backend pods:
   - Pods in `us-east-1a` must receive $\ge 98\%$ of all requests.
   - Pods in `us-east-1b` and `us-east-1c` must receive $< 2\%$ of requests.

---

## Exercise 3: Building a Resilient Spot Interruption Drain Daemon

### 1. Objective
Build an integration test simulating an AWS EC2 Spot 2-minute interruption notice, validating that a high-throughput Java Kafka consumer drains active requests, commits offsets, and shuts down cleanly within 45 seconds without losing a single message.

### 2. Implementation Tasks
1. Create a mock HTTP server simulating AWS IMDSv2:
   - Responds to `PUT /latest/api/token`.
   - Responds to `GET /latest/meta-data/spot/instance-action` with 404 initially, then switches to 200 OK returning:
     ```json
     {"action":"terminate","time":"2026-10-01T14:30:00Z"}
     ```
2. Implement `SpotDrainController.java` using `SpotInterruptionWatcher`:
   - Upon receiving the termination event, set HTTP health check `/ready` to 503 Service Unavailable.
   - Stop pulling messages from Kafka consumer (`consumer.wakeup()`).
   - Allow active worker threads up to 30 seconds to finish in-flight business calculations.
   - Flush pending Kafka producer events (`producer.flush()`).
   - Perform atomic synchronous offset commit (`consumer.commitSync()`).
   - Close database connections and exit process with code 0.
3. Test under 5,000 in-flight synthetic messages: verify **zero message duplication** and **zero dropped transactions**.

---

## Exercise 4: Benchmarking and Eliminating Linux CFS Quota Throttling

### 1. Objective
Reproduce the multi-threaded CFS quota throttling trap inside a container, quantify the resulting P99 latency degradation, and eliminate it by tuning Kubernetes limits.

### 2. Implementation Tasks
1. Create a multi-threaded compute task in Java:
   ```java
   public class ThreadedBurstTask {
       public static void main(String[] args) {
           ExecutorService pool = Executors.newFixedThreadPool(16);
           while (true) {
               long start = System.nanoTime();
               List<Future<?>> futures = new ArrayList<>();
               for (int i = 0; i < 16; i++) {
                   futures.add(pool.submit(() -> {
                       long sum = 0;
                       for (int j = 0; j < 20_000_000; j++) sum += j;
                       return sum;
                   }));
               }
               for (Future<?> f : futures) f.get();
               long durationMs = (System.nanoTime() - start) / 1_000_000;
               System.out.println("Burst Completed in: " + durationMs + "ms");
           }
       }
   }
   ```
2. Run inside Docker with CPU quota equal to 2 cores:
   ```bash
   docker run --rm --cpus=2.0 -v $(pwd):/app openjdk:21 java -cp /app ThreadedBurstTask
   ```
3. In a separate shell, monitor CFS throttling statistics:
   ```bash
   CONTAINER_ID=$(docker ps -q)
   docker exec "$CONTAINER_ID" cat /sys/fs/cgroup/cpu.stat
   ```
4. Observe the burst execution times and note that `nr_throttled` climbs rapidly.
5. Re-run without `--cpus` (relying on `--cpu-shares=2048`):
   - Observe burst latency drop from **$180\text{ms}$ down to $22\text{ms}$ ($8\times$ faster)**.
   - Verify `nr_throttled` remains at 0.
