package com.learning.jvm;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;

/**
 * Smoke test that executes the module demo entry points.
 * Ensures demo harnesses stay runnable and contributes coverage
 * for print-driven demonstration code.
 */
@DisplayName("Demo Smoke Test")
class DemoSmokeTest {

    @Test
    @DisplayName("JVM internals lab demo runs without throwing")
    void testLabDemoRuns() {
        assertDoesNotThrow(() -> JVMInternalsLab.main(new String[0]));
    }

    @Test
    @DisplayName("Elite training main runs without throwing")
    void testEliteMainRuns() {
        assertDoesNotThrow(() -> EliteJVMInternalsTraining.main(new String[0]));
    }

    @Test
    @DisplayName("Elite training demonstrate runs without throwing")
    void testEliteDemonstrateRuns() {
        assertDoesNotThrow(() -> EliteJVMInternalsTraining.demonstrate());
    }
}
