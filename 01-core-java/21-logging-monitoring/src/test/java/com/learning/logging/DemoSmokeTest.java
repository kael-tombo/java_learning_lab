package com.learning.logging;

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
    @DisplayName("Logging lab demo runs without throwing")
    void testLabDemoRuns() {
        assertDoesNotThrow(() -> Lab.main(new String[0]));
    }

    @Test
    @DisplayName("Logging monitoring training demo runs without throwing")
    void testTrainingDemoRuns() {
        assertDoesNotThrow(() -> LoggingMonitoringTraining.main(new String[0]));
    }
}
