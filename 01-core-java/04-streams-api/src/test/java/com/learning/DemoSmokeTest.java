package com.learning;

import com.learning.advanced.OptionalDemo;
import com.learning.basics.IntermediateOperationsDemo;
import com.learning.basics.StreamSourcesDemo;
import com.learning.intermediate.PeekAndDebugDemo;
import com.learning.intermediate.StatefulOperationsDemo;
import com.learning.terminal.MatchOperationsDemo;
import com.learning.terminal.ReductionOperationsDemo;
import com.learning.terminal.TerminalOperationsBasicsDemo;
import com.learning.transformation.MapOperationsDemo;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;

/**
 * Smoke test that executes every demo entry point.
 * Main covers the primary paths; the second test covers demos
 * Main does not invoke so JaCoCo sees real coverage.
 */
@DisplayName("Demo Smoke Test")
class DemoSmokeTest {

    @Test
    @DisplayName("Main demo runs without throwing")
    void testMainDemoRuns() {
        assertDoesNotThrow(() -> Main.main(new String[0]));
    }

    @Test
    @DisplayName("Elite training demo runs without throwing")
    void testEliteDemoRuns() {
        assertDoesNotThrow(EliteStreamsTraining::demonstrateAll);
    }

    @Test
    @DisplayName("Demos not covered by Main run without throwing")
    void testRemainingDemosRun() {
        assertDoesNotThrow(() -> {
            new IntermediateOperationsDemo().demonstrateIntermediateOps();
            new StreamSourcesDemo().demonstrateStreamSources();
            new OptionalDemo().demonstrateOptional();
            new com.learning.intermediate.FlatMapOperationsDemo().demonstrateFlatMap();
            new PeekAndDebugDemo().demonstratePeekAndDebug();
            new StatefulOperationsDemo().demonstrateStatefulOps();
            new MatchOperationsDemo().demonstrateMatch();
            new ReductionOperationsDemo().demonstrateReduction();
            new TerminalOperationsBasicsDemo().demonstrateTerminalOps();
            new MapOperationsDemo().demonstrateObjectMapping();
            new MapOperationsDemo().demonstrateBasicMapping();
            new MapOperationsDemo().demonstrateStringMapping();
            new MapOperationsDemo().demonstrateChainedMapping();
            new MapOperationsDemo().demonstrateNumericMapping();
            new com.learning.transformation.FlatMapOperationsDemo().demonstrateBasicFlatMap();
            new com.learning.transformation.FlatMapOperationsDemo().demonstrateFlatMapWithStrings();
            new com.learning.transformation.FlatMapOperationsDemo().demonstrateFlatMapWithObjects();
            new com.learning.transformation.FlatMapOperationsDemo().demonstrateFlatMapVsMap();
            new com.learning.transformation.FlatMapOperationsDemo().demonstrateFlatMapForCombinations();
            new com.learning.transformation.FlatMapOperationsDemo().demonstrateNestedFlatMap();
            new com.learning.transformation.FlatMapOperationsDemo().demonstrateFlatMapWithOptional();
            new com.learning.transformation.FlatMapOperationsDemo().demonstrateFlatMapPerformance();
            // Optional + filtering methods Main does not invoke
            new com.learning.optional.OptionalPatternsDemo().demonstrateOptionalConditionalLogic();
            new com.learning.optional.OptionalPatternsDemo().demonstrateOptionalStreams();
            new com.learning.optional.OptionalPatternsDemo().demonstrateOptionalCombination();
            new com.learning.optional.OptionalPatternsDemo().demonstrateOptionalPitfalls();
            new com.learning.filtering.FilterOperationsDemo().demonstrateFilterCounting();
        });
    }
}
