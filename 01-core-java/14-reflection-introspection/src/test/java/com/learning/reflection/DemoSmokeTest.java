package com.learning.reflection;

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
    @DisplayName("Reflection lab demo runs without throwing")
    void testLabDemoRuns() {
        assertDoesNotThrow(() -> ReflectionLab.main(new String[0]));
    }

    @Test
    @DisplayName("Elite training main runs without throwing")
    void testEliteMainRuns() {
        assertDoesNotThrow(() -> EliteReflectionTraining.main(new String[0]));
    }

    @Test
    @DisplayName("Elite training demonstrate runs without throwing")
    void testEliteDemonstrateRuns() {
        assertDoesNotThrow(() -> EliteReflectionTraining.demonstrate());
    }
}
