package com.learning.data;

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
    @DisplayName("Spring Data JPA training demo runs without throwing")
    void testTrainingDemoRuns() {
        assertDoesNotThrow(() -> SpringDataJpaTraining.main(new String[0]));
    }
}
