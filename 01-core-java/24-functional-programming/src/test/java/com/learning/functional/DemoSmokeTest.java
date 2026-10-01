package com.learning.functional;

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
    @DisplayName("Functional lab demo runs without throwing")
    void testLabDemoRuns() {
        assertDoesNotThrow(() -> Lab.main(new String[0]));
    }

    @Test
    @DisplayName("Functional programming training demo runs without throwing")
    void testTrainingDemoRuns() {
        assertDoesNotThrow(() -> FunctionalProgrammingTraining.main(new String[0]));
    }

    @Test
    @DisplayName("Functional strategy pattern demo runs without throwing")
    void testStrategyDemoRuns() {
        assertDoesNotThrow(FunctionalDesignPatterns::demonstrateStrategy);
    }

    @Test
    @DisplayName("Functional command pattern demo runs without throwing")
    void testCommandDemoRuns() {
        assertDoesNotThrow(FunctionalDesignPatterns::demonstrateCommand);
    }

    @Test
    @DisplayName("Functional execute-around demo runs without throwing")
    void testExecuteAroundDemoRuns() {
        assertDoesNotThrow(FunctionalDesignPatterns::demonstrateExecuteAround);
    }
}
