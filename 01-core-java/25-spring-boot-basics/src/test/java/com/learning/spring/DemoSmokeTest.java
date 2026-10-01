package com.learning.spring;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.boot.SpringApplication;
import org.springframework.context.ConfigurableApplicationContext;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;

/**
 * Smoke test that executes the module demo entry points.
 * Ensures demo harnesses stay runnable and contributes coverage
 * for print-driven demonstration code.
 */
@DisplayName("Demo Smoke Test")
class DemoSmokeTest {

    @Test
    @DisplayName("Spring Boot training app starts without throwing (random port)")
    void testTrainingDemoRuns() {
        assertDoesNotThrow(() -> {
            SpringApplication app = new SpringApplication(SpringBootTraining.class);
            app.setAdditionalProfiles("test");
            ConfigurableApplicationContext ctx = app.run(new String[0]);
            ctx.close();
        });
    }
}
