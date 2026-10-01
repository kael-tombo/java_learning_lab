package com.learning.istio;

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
    @DisplayName("Istio Linkerd lab demo runs without throwing")
    void testLabDemoRuns() {
        assertDoesNotThrow(() -> Lab.main(new String[0]));
    }
}
