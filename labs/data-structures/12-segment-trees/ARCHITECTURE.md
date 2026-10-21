# Architecture of Segment Trees in Applications

## Integration Patterns

### Basic Embedding
`java
public class DataAnalyzer {
    private final SegmentTree segmentTree;
    
    public DataAnalyzer(int[] data) {
        this.segmentTree = new RecursiveSegmentTree(data);
    }
    
    public int queryRange(int l, int r) { 
        return segmentTree.rangeSum(l, r);
    }
}
`

### Layered Architecture
`
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚      Presentation Layer      â”‚
â”‚  (REST API / CLI / GUI)     â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚      Service Layer           â”‚
â”‚  (RangeQueryService)        â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚    Data Structure Layer      â”‚
â”‚  (SegmentTree / Fenwick)    â”‚
â”œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¤
â”‚      Data Layer              â”‚
â”‚  (Arrays / Database)        â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
`

### Strategy Pattern for Range Queries
`java
public interface RangeQueryStrategy {
    int query(int l, int r);
    void update(int pos, int val);
}

public class QueryContext {
    private RangeQueryStrategy strategy;
    
    public void setStrategy(RangeQueryStrategy strategy) {
        this.strategy = strategy;
    }
    
    public int executeQuery(int l, int r) {
        return strategy.query(l, r);
    }
}
`

## Application Architecture Examples

### Real-Time Analytics Dashboard
- Maintain segment tree over time-series data
- Range queries for aggregates over time windows
- Point updates for new data points
- Lazy propagation for bulk data corrections

### Geographic Information System
- 2D segment tree over spatial grid
- Range queries for population density
- Point updates for new census data
- Nested segment trees for multi-dimensional data

## Design Decisions

1. **Array vs Node-based**: Array-based for performance, node-based for flexibility
2. **Recursive vs Iterative**: Recursive for clarity, iterative for speed
3. **Lazy vs Eager**: Lazy for range updates, eager for point updates only
4. **Generic vs Type-specific**: Generic for reusability, type-specific for performance
