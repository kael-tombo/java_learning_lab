package com.learning.java.generics;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;

/**
 * Smoke test that runs the module demo entry point so print-driven
 * demonstration code is exercised and covered.
 */
@DisplayName("Demo Smoke Test")
class DemoSmokeTest {

    @Test
    @DisplayName("Elite training demo runs without throwing")
    void testMainDemoRuns() {
        assertDoesNotThrow(() -> EliteGenericsTraining.main(new String[0]));
    }
}
