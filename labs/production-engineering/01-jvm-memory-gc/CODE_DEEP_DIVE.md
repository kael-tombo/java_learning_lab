package com.production.jvm;

import java.lang.management.*;
import java.lang.ref.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.concurrent.atomic.*;

/**
 * PRODUCTION JVM MEMORY MANAGEMENT - CODE DEEP DIVE
 * Lab 01: JVM Memory Architecture & GC Mastery
 *
 * This file demonstrates production-grade memory management patterns,
 * heap analysis techniques, and GC-friendly coding in Java.
 *
 * Topics covered:
 * 1. Heap monitoring via JMX (runtime introspection)
 * 2. Off-heap/Direct buffer pool
 * 3. Object pool pattern (reduce GC pressure)
 * 4. Weak/Soft/Phantom reference usage
 * 5. Memory-efficient data structures
 * 6. Heap dump programmatic trigger
 */
public class ProductionMemoryPatterns {

    // ─────────────────────────────────────────────────────────────────────
    // 1. RUNTIME HEAP MONITORING via JMX
    // Use this in production to alert before OOM
    // ─────────────────────────────────────────────────────────────────────

    public static class HeapMonitor {
        private static final MemoryMXBean memoryMXBean = ManagementFactory.getMemoryMXBean();
        private static final List<MemoryPoolMXBean> pools = ManagementFactory.getMemoryPoolMXBeans();

        /** Returns heap usage as a percentage 0-100 */
        public static double heapUsagePercent() {
            MemoryUsage usage = memoryMXBean.getHeapMemoryUsage();
            return (double) usage.getUsed() / usage.getMax() * 100.0;
        }

        /** Prints detailed memory report - run from /actuator or admin endpoint */
        public static void printMemoryReport() {
            System.out.println("=== JVM Memory Report ===");
            MemoryUsage heap = memoryMXBean.getHeapMemoryUsage();
            MemoryUsage nonHeap = memoryMXBean.getNonHeapMemoryUsage();

            System.out.printf("Heap:     used=%dMB, committed=%dMB, max=%dMB, usage=%.1f%%%n",
                mb(heap.getUsed()), mb(heap.getCommitted()), mb(heap.getMax()),
                (double) heap.getUsed() / heap.getMax() * 100);

            System.out.printf("Non-Heap: used=%dMB, committed=%dMB%n",
                mb(nonHeap.getUsed()), mb(nonHeap.getCommitted()));

            System.out.println("\n--- Memory Pools ---");
            for (MemoryPoolMXBean pool : pools) {
                MemoryUsage usage = pool.getUsage();
                if (usage.getMax() > 0) {
                    System.out.printf("  %-40s %dMB / %dMB (%.1f%%)%n",
                        pool.getName(),
                        mb(usage.getUsed()),
                        mb(usage.getMax()),
                        (double) usage.getUsed() / usage.getMax() * 100);
                }
            }
        }

        /** Register callback when Old Gen > threshold — production alerting */
        public static void registerOldGenAlert(double thresholdPercent, Runnable alertCallback) {
            pools.stream()
                .filter(p -> p.getName().contains("Old") || p.getName().contains("Tenured"))
                .findFirst()
                .ifPresent(oldGenPool -> {
                    MemoryUsage usage = oldGenPool.getUsage();
                    long threshold = (long) (usage.getMax() * thresholdPercent / 100);
                    oldGenPool.setUsageThreshold(threshold);

                    // Register notification listener
                    NotificationEmitter emitter = (NotificationEmitter) ManagementFactory.getMemoryMXBean();
                    emitter.addNotificationListener((notification, handback) -> {
                        if (notification.getType().equals(MemoryNotificationInfo.MEMORY_THRESHOLD_EXCEEDED)) {
                            alertCallback.run();
                        }
                    }, null, null);
                });
        }

        private static long mb(long bytes) { return bytes / 1_048_576; }
    }

    // ─────────────────────────────────────────────────────────────────────
    // 2. DIRECT BUFFER POOL — Off-heap memory management
    // Avoids GC pressure for I/O buffers; reuses buffers across requests
    // ─────────────────────────────────────────────────────────────────────

    public static class DirectBufferPool {
        private final Deque<java.nio.ByteBuffer> pool = new ArrayDeque<>();
        private final int bufferSize;
        private final int maxPoolSize;
        private final AtomicInteger allocated = new AtomicInteger(0);

        public DirectBufferPool(int bufferSize, int maxPoolSize) {
            this.bufferSize = bufferSize;
            this.maxPoolSize = maxPoolSize;
        }

        /** Borrow a direct buffer from the pool. MUST call release() after use. */
        public java.nio.ByteBuffer acquire() {
            java.nio.ByteBuffer buf = pool.pollFirst();
            if (buf == null) {
                allocated.incrementAndGet();
                buf = java.nio.ByteBuffer.allocateDirect(bufferSize);  // Off-heap!
            }
            buf.clear();
            return buf;
        }

        /** Return buffer to pool for reuse. Call in finally block! */
        public void release(java.nio.ByteBuffer buffer) {
            if (pool.size() < maxPoolSize) {
                pool.offerFirst(buffer);
            }
            // else: let it be GC'd — pool is full
        }

        public int getPoolSize() { return pool.size(); }
        public int getTotalAllocated() { return allocated.get(); }

        // Convenience — try-with-resources pattern
        public PooledBuffer borrow() {
            return new PooledBuffer(acquire(), this);
        }

        public static class PooledBuffer implements AutoCloseable {
            public final java.nio.ByteBuffer buffer;
            private final DirectBufferPool pool;

            PooledBuffer(java.nio.ByteBuffer buffer, DirectBufferPool pool) {
                this.buffer = buffer;
                this.pool = pool;
            }

            @Override
            public void close() {
                pool.release(buffer);  // Auto-return on try-with-resources exit
            }
        }
    }

    // Usage example:
    static DirectBufferPool bufferPool = new DirectBufferPool(64 * 1024, 100); // 100 × 64KB buffers

    static void handleRequest(byte[] data) {
        try (DirectBufferPool.PooledBuffer pb = bufferPool.borrow()) {
            pb.buffer.put(data);
            pb.buffer.flip();
            // process pb.buffer...
        } // buffer automatically returned to pool
    }

    // ─────────────────────────────────────────────────────────────────────
    // 3. OBJECT POOL — Reduce GC pressure for expensive objects
    // Classic pattern: database connections, parsers, serializers
    // ─────────────────────────────────────────────────────────────────────

    public interface Resettable {
        void reset();
    }

    public static class ObjectPool<T extends Resettable> {
        private final Deque<T> pool = new ConcurrentLinkedDeque<>();
        private final java.util.function.Supplier<T> factory;
        private final int maxSize;
        private final AtomicInteger size = new AtomicInteger(0);

        public ObjectPool(java.util.function.Supplier<T> factory, int maxSize) {
            this.factory = factory;
            this.maxSize = maxSize;
            // Pre-warm the pool
            for (int i = 0; i < maxSize / 2; i++) {
                pool.add(factory.get());
                size.incrementAndGet();
            }
        }

        public T borrow() {
            T obj = pool.pollFirst();
            if (obj == null) {
                obj = factory.get();
            }
            return obj;
        }

        public void returnToPool(T obj) {
            obj.reset();  // Clear state before returning
            if (size.get() < maxSize) {
                pool.offerFirst(obj);
            }
            // else: abandon — GC will handle
        }
    }

    // ─────────────────────────────────────────────────────────────────────
    // 4. WEAK/SOFT/PHANTOM REFERENCES — Memory-sensitive caching
    // ─────────────────────────────────────────────────────────────────────

    /**
     * SoftReference cache: JVM will clear entries before throwing OOM.
     * Perfect for: image caches, parsed document caches, compiled regex.
     */
    public static class SoftCache<K, V> {
        private final Map<K, SoftReference<V>> map = new ConcurrentHashMap<>();
        private final java.util.function.Function<K, V> loader;
        private final ReferenceQueue<V> refQueue = new ReferenceQueue<>();

        public SoftCache(java.util.function.Function<K, V> loader) {
            this.loader = loader;
        }

        public V get(K key) {
            expungeStaleEntries();  // Clean up GC'd references
            SoftReference<V> ref = map.get(key);
            V value = ref != null ? ref.get() : null;
            if (value == null) {
                value = loader.apply(key);
                map.put(key, new SoftReference<>(value, refQueue));
            }
            return value;
        }

        private void expungeStaleEntries() {
            Reference<? extends V> stale;
            while ((stale = refQueue.poll()) != null) {
                // Remove the stale entry (we'd need a reverse map for this in production)
                map.values().remove(stale);
            }
        }
    }

    /**
     * WeakHashMap-based cache: entries removed when key is no longer strongly referenced.
     * Perfect for: per-object metadata, class-keyed metadata.
     */
    static final Map<Object, String> objectMetadata = new WeakHashMap<>();  // Keys GC'd automatically

    /**
     * PhantomReference for cleanup after GC.
     * Perfect for: native resource cleanup, off-heap deallocation.
     */
    static class NativeResourceCleaner extends PhantomReference<Object> {
        private final long nativePointer;

        NativeResourceCleaner(Object referent, ReferenceQueue<Object> queue, long nativePointer) {
            super(referent, queue);
            this.nativePointer = nativePointer;
        }

        void cleanup() {
            // freeNativeMemory(nativePointer);  // Called after referent is GC'd
            System.out.printf("Freed native memory at 0x%x%n", nativePointer);
        }
    }

    // ─────────────────────────────────────────────────────────────────────
    // 5. MEMORY-EFFICIENT DATA STRUCTURES
    // ─────────────────────────────────────────────────────────────────────

    /**
     * Use arrays instead of ArrayList for primitive types.
     * ArrayList<Integer> → ~20 bytes per entry (header + ref + Integer box)
     * int[] → 4 bytes per entry → 5x memory reduction
     */
    static int[] efficientCounters = new int[100_000];  // vs List<Integer>

    /**
     * Compact string representation for high-cardinality data.
     * String header: ~32 bytes. For short strings that repeat, intern them.
     */
    static final Map<String, String> INTERNED_STATES = new HashMap<>();
    static {
        for (String state : new String[]{"PENDING", "ACTIVE", "CLOSED", "FAILED"}) {
            INTERNED_STATES.put(state, state.intern());  // Share one String instance
        }
    }

    // ─────────────────────────────────────────────────────────────────────
    // 6. PROGRAMMATIC HEAP DUMP — Use in emergency or via admin endpoint
    // ─────────────────────────────────────────────────────────────────────

    public static void triggerHeapDump(String filePath) throws Exception {
        com.sun.management.HotSpotDiagnosticMXBean diagBean =
            ManagementFactory.getPlatformMXBean(com.sun.management.HotSpotDiagnosticMXBean.class);
        diagBean.dumpHeap(filePath, true);  // true = live objects only
        System.out.println("Heap dump written to: " + filePath);
    }

    // ─────────────────────────────────────────────────────────────────────
    // 7. GC PAUSE MEASUREMENT — Know your actual pause impact
    // ─────────────────────────────────────────────────────────────────────

    public static class GcPauseDetector {
        private final ScheduledExecutorService executor;
        private volatile long lastCheckTime = System.currentTimeMillis();
        private final AtomicLong maxPause = new AtomicLong(0);
        private final AtomicLong pauseCount = new AtomicLong(0);

        public GcPauseDetector() {
            executor = Executors.newSingleThreadScheduledExecutor(r -> {
                Thread t = new Thread(r, "gc-pause-detector");
                t.setDaemon(true);
                return t;
            });
        }

        public void start() {
            executor.scheduleAtFixedRate(() -> {
                long now = System.currentTimeMillis();
                long gap = now - lastCheckTime;
                if (gap > 50) {  // Expected ~10ms interval, >50ms = likely GC pause
                    maxPause.updateAndGet(prev -> Math.max(prev, gap));
                    pauseCount.incrementAndGet();
                    System.out.printf("[GC-PAUSE-DETECTOR] Detected pause: %dms%n", gap);
                }
                lastCheckTime = now;
            }, 10, 10, TimeUnit.MILLISECONDS);  // Check every 10ms
        }

        public long getMaxPauseMs() { return maxPause.get(); }
        public long getPauseCount() { return pauseCount.get(); }
    }
}
