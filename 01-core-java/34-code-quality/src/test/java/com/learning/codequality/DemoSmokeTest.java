package com.learning.codequality;

import com.learning.quality.CodeQualityTraining;
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
    @DisplayName("Lab demo runs without throwing")
    void testLabDemoRuns() {
        assertDoesNotThrow(() -> Lab.main(new String[0]));
    }

    @Test
    @DisplayName("Code quality training demo runs without throwing")
    void testTrainingDemoRuns() {
        assertDoesNotThrow(() -> CodeQualityTraining.main(new String[0]));
    }
}
