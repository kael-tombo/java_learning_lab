# Architecture of Fenwick Tree in Applications

## Integration Patterns

### Standalone Usage
`java
public class FrequencyTracker {
    private final FenwickTree ft;
    
    public void increment(int value) {
        ft.add(value, 1);
    }
    
    public int countLessThan(int value) {
        return ft.sum(value - 1);
    }
}
`

### Service Layer
`java
@Service
public class AnalyticsService {
    private final FenwickTree eventCounts;
    
    public void recordEvent(String type) {
        int id = eventTypeId(type);
        eventCounts.add(id, 1);
    }
    
    public long cumulativeEvents(List<String> types) {
        return types.stream()
            .mapToInt(this::eventTypeId)
            .map(id -> eventCounts.sum(id))
            .sum();
    }
}
`

### Layered Architecture
`
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚      Application Layer       â”‚
â”‚  (REST Controllers / CLI)   â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚      Service Layer           â”‚
â”‚  (Analytics, Metrics)       â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚      Data Structure Layer    â”‚
â”‚  (FenwickTree, FenwickTree2D)â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚      Data Storage            â”‚
â”‚  (In-memory / Serialized)   â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
`

## Design Decision: Data Type

- **int[]**: For small values, limited to 2B
- **long[]**: For large values or many operations
- **AtomicIntegerArray**: For concurrent updates
- **double[]**: For floating-point accumulations

## Architecture Patterns

BIT is often part of a larger data pipeline:
1. Data ingestion → BIT updates
2. Query processing → BIT prefix sums
3. Result aggregation → Response formatting
