package com.learning.patterns;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;

/**
 * Smoke test that runs the module demo entry points so print-driven
 * demonstration code is exercised and covered.
 */
@DisplayName("Demo Smoke Test")
class DemoSmokeTest {

    @Test
    @DisplayName("Design patterns lab demo runs without throwing")
    void testLabDemoRuns() {
        assertDoesNotThrow(() -> DesignPatternsLab.main(new String[0]));
    }

    @Test
    @DisplayName("Elite training demo runs without throwing")
    void testEliteDemoRuns() {
        assertDoesNotThrow(() -> EliteDesignPatternsTraining.main(new String[0]));
    }
}
