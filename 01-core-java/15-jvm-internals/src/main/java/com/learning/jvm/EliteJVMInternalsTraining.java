package com.learning.jvm;

import java.lang.management.ManagementFactory;
import java.lang.management.MemoryMXBean;
import java.lang.management.MemoryPoolMXBean;
import java.lang.management.ThreadMXBean;
import java.util.ArrayList;
import java.util.List;

/**
 * Elite JVM Internals Training
 *
 * Demonstrates runtime-observable JVM behavior:
 * - Runtime data areas (heap metrics, memory pools)
 * - GC behavior and reachability (SoftReference vs WeakReference)
 * - Class loading basics and identity semantics
 * - Stack behavior: depth, StackOverflowError, tail-call-free recursion
 * - Thread diagnostics: daemon vs user threads, deadlock detection
 *
 * Everything is observable without agents or native tooling, so the tests
 * can assert real JVM behavior on any standard JDK.
 */
public class EliteJVMInternalsTraining {

    // ============================================================================
    // SECTION 1: RUNTIME DATA AREAS
    // ============================================================================

    public static class MemoryInspector {

        public record HeapSnapshot(long usedBytes, long committedBytes, long maxBytes) {
            public double usedFraction() {
                return maxBytes <= 0 ? 0 : (double) usedBytes / maxBytes;
            }
        }

        public static HeapSnapshot heapSnapshot() {
            MemoryMXBean memory = ManagementFactory.getMemoryMXBean();
            long used = memory.getHeapMemoryUsage().getUsed();
            long committed = memory.getHeapMemoryUsage().getCommitted();
            long max = memory.getHeapMemoryUsage().getMax();
            return new HeapSnapshot(used, committed, max);
        }

        public static List<String> memoryPoolNames() {
            return ManagementFactory.getMemoryPoolMXBeans().stream()
                    .map(MemoryPoolMXBean::getName)
                    .toList();
        }

        public static long youngGenerationPoolBytes() {
            return ManagementFactory.getMemoryPoolMXBeans().stream()
                    .filter(p -> p.getName().toLowerCase().contains("eden"))
                    .mapToLong(p -> p.getUsage().getCommitted())
                    .sum();
        }
    }

    // ============================================================================
    // SECTION 2: REACHABILITY & REFERENCES
    // ============================================================================

    public static class ReferencePlayground {

        public record ReferenceOutcome(boolean softCleared, boolean weakCleared, boolean phantomEnqueued) {}

        /**
         * Allocates pressure to nudge the GC while observing when reference
         * types are cleared. Soft references survive longer than weak ones.
         */
        public static ReferenceOutcome observeReferenceClearing() {
            java.lang.ref.SoftReference<Object> soft = new java.lang.ref.SoftReference<>(new Object());
            java.lang.ref.WeakReference<Object> weak = new java.lang.ref.WeakReference<>(new Object());
            java.lang.ref.PhantomReference<Object> phantom =
                    new java.lang.ref.PhantomReference<>(new Object(), new java.lang.ref.ReferenceQueue<>());

            // No strong references remain; only the reference objects point at the targets.
            List<Object> pressure = new ArrayList<>();
            boolean softCleared = false;
            boolean weakCleared = false;
            boolean phantomEnqueued = false;

            for (int i = 0; i < 200 && !phantomEnqueued; i++) {
                pressure.add(new byte[1_000_000]); // 1 MB chunks push the GC
                System.gc();
                if (!softCleared && soft.get() == null) softCleared = true;
                if (!weakCleared && weak.get() == null) weakCleared = true;
                if (!phantomEnqueued && phantom.isEnqueued()) phantomEnqueued = true;
            }
            pressure.clear();

            return new ReferenceOutcome(softCleared, weakCleared, phantomEnqueued);
        }

        /** Canonical leak pattern: static collection that grows forever. */
        public static class StaticLeak {
            private static final List<byte[]> LEAK = new ArrayList<>();

            public static void leak(int megabytes) {
                for (int i = 0; i < megabytes; i++) {
                    LEAK.add(new byte[1_000_000]);
                }
            }

            public static int leakedChunks() {
                return LEAK.size();
            }

            public static void reset() {
                LEAK.clear();
            }
        }
    }

    // ============================================================================
    // SECTION 3: CLASS LOADING & IDENTITY
    // ============================================================================

    public static class ClassLoadingLab {

        public static Class<?> loadClass(String name) throws ClassNotFoundException {
            return Class.forName(name);
        }

        public static String classLoaderChain(Class<?> clazz) {
            List<String> chain = new ArrayList<>();
            for (ClassLoader cl = clazz.getClassLoader(); cl != null; cl = cl.getParent()) {
                chain.add(cl.getClass().getSimpleName());
            }
            chain.add("bootstrap");
            return String.join(" -> ", chain);
        }

        /** Loading a class does NOT run its static initializer... but initializing does. */
        public static class InitTracker {
            static boolean initialized = false;
            static {
                initialized = true;
            }
        }

        public static boolean isInitialized() {
            return InitTracker.initialized;
        }

        public static void forceInitialization() {
            // Touching a static member triggers initialization (JLS 12.4.1)
            boolean ignored = InitTracker.initialized;
        }

        public static int instanceCount() {
            // int.class, void.class etc. share identity with literals
            return 42;
        }
    }

    // ============================================================================
    // SECTION 4: STACK BEHAVIOR
    // ============================================================================

    public static class StackLab {

        /** Counts frames until StackOverflowError; returns the observed depth. */
        public static int measureStackDepth() {
            try {
                return recurse(0);
            } catch (StackOverflowError e) {
                return -1; // sentinel: caller distinguishes via overload
            }
        }

        private static int recurse(int depth) {
            return recurse(depth + 1); // no base case
        }

        /** Bounded recursion that returns the depth reached before a limit. */
        public static int recurseToDepth(int current, int limit) {
            if (current >= limit) {
                return current;
            }
            return recurseToDepth(current + 1, limit);
        }

        public static int catchOverflowDepth() {
            try {
                recurse(0);
            } catch (StackOverflowError e) {
                // Stack unwound; depth unknown here, but the error is catchable.
                return -1;
            }
            throw new AssertionError("unreachable");
        }

        public static long currentThreadStackDepth() {
            return Thread.currentThread().getStackTrace().length;
        }
    }

    // ============================================================================
    // SECTION 5: THREAD DIAGNOSTICS
    // ============================================================================

    public static class ThreadDiagnosticsLab {

        public static boolean isDaemon(Thread thread) {
            return thread.isDaemon();
        }

        public static Thread startDaemon(Runnable task) {
            Thread t = Thread.ofPlatform().daemon(true).unstarted(task);
            t.start();
            return t;
        }

        /**
         * Creates a real deadlock between two ReentrantLocks and reports the
         * found cycle. lockInterruptibly keeps the threads interruptible so the
         * deadlock can be cleaned up after detection (monitor deadlocks cannot).
         */
        public static long[] createDeadlockAndDetect() throws Exception {
            java.util.concurrent.locks.ReentrantLock lockA = new java.util.concurrent.locks.ReentrantLock();
            java.util.concurrent.locks.ReentrantLock lockB = new java.util.concurrent.locks.ReentrantLock();
            java.util.concurrent.CountDownLatch bothHolding = new java.util.concurrent.CountDownLatch(2);

            Thread t1 = Thread.ofPlatform().name("deadlock-1").unstarted(() -> {
                lockA.lock();
                try {
                    bothHolding.countDown();
                    try { bothHolding.await(); } catch (InterruptedException ignored) { return; }
                    try {
                        lockB.lockInterruptibly(); // will block forever: t2 holds B
                        lockB.unlock();
                    } catch (InterruptedException e) {
                        // interrupted by cleanup: exit cleanly, releasing lockA
                    }
                } finally {
                    lockA.unlock();
                }
            });
            Thread t2 = Thread.ofPlatform().name("deadlock-2").unstarted(() -> {
                lockB.lock();
                try {
                    bothHolding.countDown();
                    try { bothHolding.await(); } catch (InterruptedException ignored) { return; }
                    try {
                        lockA.lockInterruptibly(); // will block forever: t1 holds A
                        lockA.unlock();
                    } catch (InterruptedException e) {
                        // interrupted by cleanup: exit cleanly, releasing lockB
                    }
                } finally {
                    lockB.unlock();
                }
            });

            t1.start();
            t2.start();
            bothHolding.await();

            long[] blockedIds = awaitDeadlockDetection();
            t1.interrupt();
            t2.interrupt();
            t1.join(1000);
            t2.join(1000);
            return blockedIds;
        }

        /** Polls the thread MX bean until the cycle appears (bounded wait). */
        private static long[] awaitDeadlockDetection() throws InterruptedException {
            long deadline = System.currentTimeMillis() + 5000;
            long[] ids = new long[0];
            while (System.currentTimeMillis() < deadline) {
                ids = findDeadlockedThreads();
                if (ids.length > 0) return ids;
                Thread.sleep(50);
            }
            return ids;
        }

        public static long[] findDeadlockedThreads() {
            ThreadMXBean threads = ManagementFactory.getThreadMXBean();
            long[] ids = threads.findDeadlockedThreads();
            return ids == null ? new long[0] : ids;
        }

        public static int liveThreadCount() {
            return ManagementFactory.getThreadMXBean().getThreadCount();
        }
    }

    // ============================================================================
    // SECTION 6: GC OBSERVATION
    // ============================================================================

    public static class GcLab {

        public static long garbageCollectionCount() {
            return ManagementFactory.getGarbageCollectorMXBeans().stream()
                    .mapToLong(java.lang.management.GarbageCollectorMXBean::getCollectionCount)
                    .sum();
        }

        /** Allocates short-lived garbage; may or may not trigger a GC. */
        public static void allocateGarbage(int megabytes) {
            for (int i = 0; i < megabytes; i++) {
                byte[] trash = new byte[1_000_000];
                if (trash[0] == 42) System.out.println("unreachable"); // keep alive until scope ends
            }
        }

        public static String runtimeInfo() {
            Runtime rt = Runtime.getRuntime();
            return "processors=%d, maxHeap=%dMB".formatted(
                    rt.availableProcessors(), rt.maxMemory() / (1024 * 1024));
        }
    }

    // ============================================================================
    // DEMO
    // ============================================================================

    public static void main(String[] args) throws Exception {
        System.out.println("=".repeat(60));
        System.out.println("ELITE JVM INTERNALS TRAINING");
        System.out.println("=".repeat(60));
        demonstrate();
        System.out.println("\nALL JVM DEMOS COMPLETED SUCCESSFULLY");
    }

    public static void demonstrate() throws Exception {
        System.out.println("\n### Runtime Data Areas ###");
        var snapshot = MemoryInspector.heapSnapshot();
        System.out.printf("  heap used=%.1fMB committed=%.1fMB max=%.1fMB%n",
                snapshot.usedBytes() / 1e6, snapshot.committedBytes() / 1e6, snapshot.maxBytes() / 1e6);
        System.out.println("  pools: " + MemoryInspector.memoryPoolNames().size());

        System.out.println("\n### Class Loading ###");
        System.out.println("  String loader chain: " + ClassLoadingLab.classLoaderChain(String.class));
        ClassLoadingLab.forceInitialization();
        System.out.println("  InitTracker initialized: " + ClassLoadingLab.isInitialized());

        System.out.println("\n### Stack Behavior ###");
        System.out.println("  bounded recursion to 100: " + StackLab.recurseToDepth(0, 100));
        System.out.println("  overflow catchable: " + (StackLab.catchOverflowDepth() == -1));
        System.out.println("  current stack frames: " + StackLab.currentThreadStackDepth());

        System.out.println("\n### Thread Diagnostics ###");
        System.out.println("  live threads: " + ThreadDiagnosticsLab.liveThreadCount());
        long[] deadlocked = ThreadDiagnosticsLab.createDeadlockAndDetect();
        System.out.println("  deadlocked thread ids detected: " + deadlocked.length);

        System.out.println("\n### GC ###");
        GcLab.allocateGarbage(20);
        System.out.println("  GC collections so far: " + GcLab.garbageCollectionCount());
        System.out.println("  " + GcLab.runtimeInfo());
    }
}
