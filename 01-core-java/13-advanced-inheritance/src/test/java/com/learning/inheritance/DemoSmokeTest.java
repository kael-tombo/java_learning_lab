package com.learning.inheritance;

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
    @DisplayName("Advanced inheritance lab demo runs without throwing")
    void testLabDemoRuns() {
        assertDoesNotThrow(() -> AdvancedInheritanceLab.main(new String[0]));
    }
}
