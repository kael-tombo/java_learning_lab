package com.learning;

import com.learning.custom.CustomCollectionExample;
import com.learning.lists.ArrayListDemo;
import com.learning.lists.CopyOnWriteArrayListDemo;
import com.learning.lists.LinkedListDemo;
import com.learning.lists.ListComparatorDemo;
import com.learning.lists.ListInterfaceDemo;
import com.learning.maps.ConcurrentHashMapDemo;
import com.learning.maps.HashMapDemo;
import com.learning.maps.LinkedHashMapDemo;
import com.learning.maps.MapInterfaceDemo;
import com.learning.maps.TreeMapDemo;
import com.learning.queues.BlockingQueueBasicsDemo;
import com.learning.queues.DequeDemo;
import com.learning.queues.PriorityQueueDemo;
import com.learning.queues.QueueInterfaceDemo;
import com.learning.sets.HashSetDemo;
import com.learning.sets.LinkedHashSetDemo;
import com.learning.sets.SetInterfaceDemo;
import com.learning.sets.TreeSetDemo;
import com.learning.utilities.CollectionsUtilityDemo;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertDoesNotThrow;

/**
 * Smoke test that executes every demo entry point.
 * Demo classes are print-driven by design; running them keeps
 * them runnable and gives JaCoCo real coverage.
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
        assertDoesNotThrow(EliteCollectionsTraining::demonstrateEliteCollectionsTraining);
    }

    @Test
    @DisplayName("All individual demos run without throwing")
    void testAllDemosRun() {
        assertDoesNotThrow(() -> {
            new ListInterfaceDemo().demonstrateLists();
            new ArrayListDemo().demonstrateArrayList();
            new LinkedListDemo().demonstrateLinkedList();
            new CopyOnWriteArrayListDemo().demonstrateCopyOnWriteArrayList();
            new ListComparatorDemo().demonstrateComparators();
            new HashSetDemo().demonstrateHashSet();
            new LinkedHashSetDemo().demonstrateLinkedHashSet();
            new TreeSetDemo().demonstrateTreeSet();
            new SetInterfaceDemo().demonstrateSets();
            new HashMapDemo().demonstrateHashMap();
            new LinkedHashMapDemo().demonstrateLinkedHashMap();
            new TreeMapDemo().demonstrateTreeMap();
            new MapInterfaceDemo().demonstrateMaps();
            new ConcurrentHashMapDemo().demonstrateConcurrentHashMap();
            new QueueInterfaceDemo().demonstrateQueues();
            new PriorityQueueDemo().demonstratePriorityQueue();
            new DequeDemo().demonstrateDeque();
            new BlockingQueueBasicsDemo().demonstrateBlockingQueue();
            new CustomCollectionExample().demonstrateCustomCollection();
            new CollectionsUtilityDemo().demonstrateUtilities();
        });
    }
}
