# CODE DEEP DIVE: Microservices Scaling Patterns
## Lab 06 | Production Engineering Academy

---

## Pattern 1: Production gRPC ManagedChannel Pool with Client-Side Load Balancing

```java
package com.learning.production.lab06;

import io.grpc.ManagedChannel;
import io.grpc.ManagedChannelBuilder;
import io.grpc.netty.shaded.io.grpc.netty.NettyChannelBuilder;

import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Production-tested gRPC Channel Pool.
 * Combines DNS-based round-robin endpoint resolution with a multi-socket TCP pool.
 */
public class GrpcChannelPool implements AutoCloseable {
    private final ManagedChannel[] channels;
    private final AtomicInteger counter = new AtomicInteger(0);
    private final int poolSize;

    public GrpcChannelPool(String targetServiceDns, int port, int poolSize) {
        this.poolSize = poolSize;
        this.channels = new ManagedChannel[poolSize];

        String target = String.format("dns:///%s:%d", targetServiceDns, port);

        for (int i = 0; i < poolSize; i++) {
            this.channels[i] = NettyChannelBuilder.forTarget(target)
                    // 1. Client-side round robin across discovered pod IPs
                    .defaultLoadBalancingPolicy("round_robin")
                    // 2. Cleartext for internal mesh (or use .useTransportSecurity() with mTLS)
                    .usePlaintext()
                    // 3. Keepalive configuration to detect zombie sockets / AWS NAT idle drops
                    .keepAliveTime(30, TimeUnit.SECONDS)
                    .keepAliveTimeout(5, TimeUnit.SECONDS)
                    .keepAliveWithoutCalls(true)
                    // 4. Message size limits to prevent out of memory attacks
                    .maxInboundMessageSize(16 * 1024 * 1024) // 16 MB
                    // 5. Idle timeout
                    .idleTimeout(5, TimeUnit.MINUTES)
                    .build();
        }
    }

    /**
     * Round-robin selection across TCP channels.
     */
    public ManagedChannel getChannel() {
        int index = Math.abs(counter.getAndIncrement() % poolSize);
        return channels[index];
    }

    @Override
    public void close() {
        for (ManagedChannel channel : channels) {
            try {
                channel.shutdown().awaitTermination(5, TimeUnit.SECONDS);
            } catch (InterruptedException ignored) {
                channel.shutdownNow();
            }
        }
    }
}
```

---

## Pattern 2: Peak EWMA Load Balancer Implementation (Power of Two Random Choices)

```java
package com.learning.production.lab06;

import java.util.List;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.atomic.AtomicLong;

public class PeakEwmaLoadBalancer {
    private static final double DECAY_FACTOR = 0.15; // Moving average decay weight

    public record Endpoint(String address, AtomicLong activeRequests, AtomicLong latencyEwmaNanos) {
        public void recordSuccess(long durationNanos) {
            activeRequests.decrementAndGet();
            latencyEwmaNanos.updateAndGet(old -> (long) (old * (1 - DECAY_FACTOR) + durationNanos * DECAY_FACTOR));
        }

        public double score() {
            // Score = Latency * (ActiveRequests + 1)
            return latencyEwmaNanos.get() * (activeRequests.get() + 1.0);
        }
    }

    /**
     * Power of Two Choices (P2C) algorithm.
     */
    public static Endpoint selectBestEndpoint(List<Endpoint> endpoints) {
        int size = endpoints.size();
        if (size == 0) throw new IllegalStateException("No available endpoints");
        if (size == 1) return endpoints.get(0);

        int idx1 = ThreadLocalRandom.current().nextInt(size);
        int idx2 = ThreadLocalRandom.current().nextInt(size);
        while (idx2 == idx1) {
            idx2 = ThreadLocalRandom.current().nextInt(size);
        }

        Endpoint e1 = endpoints.get(idx1);
        Endpoint e2 = endpoints.get(idx2);

        // Pick the endpoint with lowest moving load score
        Endpoint selected = (e1.score() <= e2.score()) ? e1 : e2;
        selected.activeRequests().incrementAndGet();
        return selected;
    }
}
```
