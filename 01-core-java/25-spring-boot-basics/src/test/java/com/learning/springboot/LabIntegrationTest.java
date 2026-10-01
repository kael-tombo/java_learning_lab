package com.learning.springboot;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;

/**
 * Smoke test that executes all Lab demonstration methods.
 * Ensures conceptual demos stay runnable and contributes coverage.
 */
@DisplayName("Lab Demo Smoke Test")
class LabIntegrationTest {

    @Test
    @DisplayName("Lab main runs all conceptual demos without throwing")
    void testLabMainRuns() {
        assertDoesNotThrow(() -> Lab.main(new String[0]));
    }

    @Test
    @DisplayName("Individual demo methods execute without throwing")
    void testIndividualDemosRun() {
        assertDoesNotThrow(() -> {
            Lab.dependencyInjection();
            Lab.autoConfiguration();
            Lab.embeddedServer();
            Lab.startersAndProperties();
            Lab.actuatorEndpoints();
        });
    }
}