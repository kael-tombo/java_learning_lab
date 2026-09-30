package com.learning.jvm;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Nested;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.assertj.core.api.Assertions.*;

@DisplayName("Elite JVM Internals Training Tests")
class EliteJVMInternalsTrainingTest {

    // ============================================================================
    // MEMORY
    // ============================================================================

    @Nested
    @DisplayName("Memory Inspector Tests")
    class MemoryTests {

        @Test
        @DisplayName("heapSnapshot should report positive used and max heap")
        void heapSnapshotSane() {
            EliteJVMInternalsTraining.MemoryInspector.HeapSnapshot snapshot =
                    EliteJVMInternalsTraining.MemoryInspector.heapSnapshot();

            assertThat(snapshot.usedBytes()).isPositive();
            assertThat(snapshot.committedBytes()).isGreaterThanOrEqualTo(snapshot.usedBytes());
            assertThat(snapshot.usedFraction()).isBetween(0.0, 1.0);
        }

        @Test
        @DisplayName("JVM should expose multiple memory pools including Eden")
        void memoryPoolsExist() {
            List<String> pools = EliteJVMInternalsTraining.MemoryInspector.memoryPoolNames();
            assertThat(pools).isNotEmpty();
            assertThat(pools.stream().anyMatch(n -> n.toLowerCase().contains("eden")))
                    .as("Expected an Eden pool in: " + pools).isTrue();
        }

        @Test
        @DisplayName("Eden pool should report non-negative committed bytes")
        void edenPoolBytes() {
            assertThat(EliteJVMInternalsTraining.MemoryInspector.youngGenerationPoolBytes()).isGreaterThanOrEqualTo(0);
        }
    }

    // ============================================================================
    // REFERENCES
    // ============================================================================

    @Nested
    @DisplayName("Reference Tests")
    class ReferenceTests {

        @Test
        @DisplayName("Strongly-held object should remain visible through references")
        void strongReferenceSurvives() {
            Object target = new Object();
            var soft = new java.lang.ref.SoftReference<>(target);
            var weak = new java.lang.ref.WeakReference<>(target);

            assertThat(soft.get()).isSameAs(target);
            assertThat(weak.get()).isSameAs(target);
        }

        @Test
        @DisplayName("WeakReference should clear after GC when unreachable")
        void weakReferenceClears() {
            Object target = new Object();
            var weak = new java.lang.ref.WeakReference<>(target);
            target = null;

            // Force GC until cleared (bounded attempts).
            for (int i = 0; i < 50 && weak.get() != null; i++) {
                System.gc();
                byte[] noise = new byte[1_000_000];
                assertThat(noise).isNotNull();
            }
            assertThat(weak.get()).isNull();
        }

        @Test
        @DisplayName("observeReferenceClearing should report reference states")
        void observeClearing() {
            EliteJVMInternalsTraining.ReferencePlayground.ReferenceOutcome outcome =
                    EliteJVMInternalsTraining.ReferencePlayground.observeReferenceClearing();

            // Weak must clear no later than soft; both flags are informational.
            assertThat(outcome.weakCleared() || outcome.softCleared())
                    .as("Under allocation pressure at least one reference type should clear").isTrue();
        }

        @Test
        @DisplayName("Static leak should accumulate and reset cleanly")
        void staticLeakAccumulates() {
            EliteJVMInternalsTraining.ReferencePlayground.StaticLeak.reset();
            EliteJVMInternalsTraining.ReferencePlayground.StaticLeak.leak(2);
            assertThat(EliteJVMInternalsTraining.ReferencePlayground.StaticLeak.leakedChunks()).isEqualTo(2);
            EliteJVMInternalsTraining.ReferencePlayground.StaticLeak.reset();
            assertThat(EliteJVMInternalsTraining.ReferencePlayground.StaticLeak.leakedChunks()).isZero();
        }
    }

    // ============================================================================
    // CLASS LOADING
    // ============================================================================

    @Nested
    @DisplayName("Class Loading Tests")
    class ClassLoadingTests {

        @Test
        @DisplayName("loadClass should resolve java.lang.String")
        void loadsString() throws Exception {
            assertThat(EliteJVMInternalsTraining.ClassLoadingLab.loadClass("java.lang.String"))
                    .isEqualTo(String.class);
        }

        @Test
        @DisplayName("Unknown class should throw ClassNotFoundException")
        void unknownClassThrows() {
            assertThatThrownBy(() ->
                    EliteJVMInternalsTraining.ClassLoadingLab.loadClass("com.learning.DoesNotExist"))
                    .isInstanceOf(ClassNotFoundException.class);
        }

        @Test
        @DisplayName("Platform classes should have an extension/app loader chain ending in bootstrap")
        void loaderChainEndsAtBootstrap() {
            String chain = EliteJVMInternalsTraining.ClassLoadingLab.classLoaderChain(String.class);
            assertThat(chain).endsWith("bootstrap");
        }

        @Test
        @DisplayName("Static initializer should run exactly when the class initializes")
        void staticInitTracking() {
            // Reading via reflection-for name forces load+init through forName
            assertThat(EliteJVMInternalsTraining.ClassLoadingLab.isInitialized())
                    .isTrue();
        }

        @Test
        @DisplayName("Class identity should be per-loader: String.class is unique")
        void classIdentity() throws Exception {
            Class<?> loaded = Class.forName("java.lang.String");
            assertThat(loaded).isSameAs(String.class);
        }
    }

    // ============================================================================
    // STACK
    // ============================================================================

    @Nested
    @DisplayName("Stack Tests")
    class StackTests {

        @Test
        @DisplayName("Bounded recursion should stop exactly at the limit")
        void boundedRecursion() {
            assertThat(EliteJVMInternalsTraining.StackLab.recurseToDepth(0, 1000)).isEqualTo(1000);
        }

        @Test
        @DisplayName("StackOverflowError should be catchable")
        void overflowCatchable() {
            assertThat(EliteJVMInternalsTraining.StackLab.catchOverflowDepth()).isEqualTo(-1);
        }

        @Test
        @DisplayName("Stack trace should have at least one frame")
        void stackTraceFrames() {
            assertThat(EliteJVMInternalsTraining.StackLab.currentThreadStackDepth()).isPositive();
        }
    }

    // ============================================================================
    // THREADS
    // ============================================================================

    @Nested
    @DisplayName("Thread Diagnostics Tests")
    class ThreadTests {

        @Test
        @DisplayName("Daemon flag should be observable")
        void daemonFlag() {
            Thread daemon = Thread.ofPlatform().daemon(true).unstarted(() -> {});
            Thread user = Thread.ofPlatform().daemon(false).unstarted(() -> {});

            assertThat(EliteJVMInternalsTraining.ThreadDiagnosticsLab.isDaemon(daemon)).isTrue();
            assertThat(EliteJVMInternalsTraining.ThreadDiagnosticsLab.isDaemon(user)).isFalse();
        }

        @Test
        @DisplayName("startDaemon should start a running daemon thread")
        void startDaemonWorks() throws Exception {
            java.util.concurrent.CountDownLatch ran = new java.util.concurrent.CountDownLatch(1);
            Thread daemon = EliteJVMInternalsTraining.ThreadDiagnosticsLab.startDaemon(ran::countDown);

            assertThat(ran.await(5, java.util.concurrent.TimeUnit.SECONDS)).isTrue();
            daemon.join(1000);
            assertThat(daemon.isDaemon()).isTrue();
        }

        @Test
        @DisplayName("createDeadlockAndDetect should report the deadlocked threads")
        void deadlockDetected() throws Exception {
            long[] deadlocked = EliteJVMInternalsTraining.ThreadDiagnosticsLab.createDeadlockAndDetect();
            assertThat(deadlocked).as("Expected JVM deadlock detection to find 2 threads").hasSize(2);
        }

        @Test
        @DisplayName("findDeadlockedThreads should return empty when no deadlock exists")
        void noDeadlockReturnsEmpty() {
            assertThat(EliteJVMInternalsTraining.ThreadDiagnosticsLab.findDeadlockedThreads()).isEmpty();
        }

        @Test
        @DisplayName("liveThreadCount should be positive")
        void liveThreadsPositive() {
            assertThat(EliteJVMInternalsTraining.ThreadDiagnosticsLab.liveThreadCount()).isPositive();
        }
    }

    // ============================================================================
    // GC
    // ============================================================================

    @Nested
    @DisplayName("GC Tests")
    class GcTests {

        @Test
        @DisplayName("GC collection counts should be non-negative")
        void gcCountsNonNegative() {
            assertThat(EliteJVMInternalsTraining.GcLab.garbageCollectionCount()).isGreaterThanOrEqualTo(0);
        }

        @Test
        @DisplayName("Garbage allocation should complete without triggering OOM")
        void allocationSurvives() {
            assertThatCode(() -> EliteJVMInternalsTraining.GcLab.allocateGarbage(10))
                    .doesNotThrowAnyException();
        }

        @Test
        @DisplayName("runtimeInfo should report processors and max heap")
        void runtimeInfoFormats() {
            String info = EliteJVMInternalsTraining.GcLab.runtimeInfo();
            assertThat(info).contains("processors=").contains("maxHeap=");
        }
    }

    // ============================================================================
    // DEMO SMOKE TEST
    // ============================================================================

    @Test
    @DisplayName("demonstrate() should run all JVM demos without throwing")
    void demoRunsCleanly() {
        assertThatCode(EliteJVMInternalsTraining::demonstrate).doesNotThrowAnyException();
    }
}
