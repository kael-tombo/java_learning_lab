# Visual Guide: Cassandra NoSQL

## Architecture Diagrams

### System Overview
`
   Client Application
         |
         v
   +-----+-----+
   |  Router   |     â† Consistent hash ring
   +-----+-----+
         |
    +----+----+----+----+
    |    |    |    |    |
    v    v    v    v    v
  +--+  +--+  +--+  +--+
  |N0|  |N1|  |N2|  |N3|  â† Database nodes
  +--+  +--+  +--+  +--+
    |    |    |    |
    v    v    v    v
  +--+  +--+  +--+  +--+
  |R0|  |R1|  |R2|  |R3|  â† Replicas
  +--+  +--+  +--+  +--+
`

### Consistent Hashing Ring
`
            hash(node_A)
                  |
         .--------+--------.
        /                   \
       |     Node A          |
       |    vnodes: a1,a2    |
       |                     |
  .----+----.          .----+----.
  | Node D  |          | Node B  |
  | d1,d2   |          | b1,b2   |
  '----+----'          '----+----'
       |                     |
       |     Node C          |
       |    c1,c2            |
        \                   /
         '--------+--------'
                  |
            hash(key_K) → Node B (nearest clockwise)
`

### Write Flow
`
Client → API Gateway → Router (hash routing key)
                             |
                     +-------v--------+
                     | Find Node       |  hash(key) → node-id
                     +-------+--------+
                             |
                     +-------v--------+
                     | Primary Node    |  Write to WAL
                     +-------+--------+
                             |
                    +--------+--------+
                    |                  |
                    v                  v
              +-----------+    +-----------+
              | Replica A |    | Replica B |  Async replication
              +-----------+    +-----------+

              Client â† Acknowledged (after quorum)
`

### Read Flow (Single Node)
`
Client → API Gateway → Router (extract routing key)
                             |
                     +-------v--------+
                     | Identify Node    |
                     +-------+--------+
                             |
                     +-------v--------+
                     | Read from        |
                     | available node   |
                     +-------+--------+
                             |
                     +-------v--------+
                     | Return result    |
                     +----------------+
`

### Scatter-Gather Flow
`
Client → Query without routing key
                     |
             +-------v--------+
             | Broadcast to    |
             | ALL nodes       |
             +-------+--------+
                     |
        +-----------+-----------+
        |           |           |
        v           v           v
    +-------+ +-------+ +-------+
    |Node 0 | |Node 1 | |Node N |   Parallel execution
    +-------+ +-------+ +-------+
        |           |           |
        +-----------+-----------+
                     |
             +-------v--------+
             | Merge & Sort    |
             +-------+--------+
                     |
             +-------v--------+
             | Return merged   |
             | result          |
             +----------------+
`

### Rebalancing Process
`
Before: [N0:80%] [N1:40%] [N2:35%] [N3:45%]
                   |
                   ▼  (add N4)
                   |
During: [N0:60%] [N1:40%] [N2:35%] [N3:45%] [N4:20%]
                   │
                   ▼
After:  [N0:50%] [N1:40%] [N2:35%] [N3:35%] [N4:40%]
`

### Comparison: Range vs Hash Distribution
`
Range Distribution:          Hash Distribution:
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â” â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”
│ N0     │ N1     │ N2     │ │ N0     │ N1     │ N2     │
│ A-D    │ E-H    │ I-L    │ │ 7A3F   │ B2C1   │ 9E8D   │
│ M-P    │ Q-T    │ U-Z    │ │ 1B4A   │ 5C9F   │ 3D7E   │
├────────┴────────┴────────┤ ├────────┴────────┴────────┤
│ Good: Range queries fast  │ │ Good: Even distribution  │
│ Bad: Hotspots on new data │ │ Bad: Cross-node ranges   │
└───────────────────────────┘ └──────────────────────────┘
`
"@

    # INTERNALS
    Write-Md System.Collections.Hashtable "INTERNALS.md" @"
# Internals: Cassandra NoSQL

## Internal Architecture

### Component Diagram
`
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
│                    Router Layer                         │
│  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” │
│  │Hash Ring │  │Partition │  │Scatter-Gather        │ │
│  │Manager   │  │Manager   │  │Engine                │ │
│  └──────────┘  └──────────┘  └──────────────────────┘ │
│  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” │
│  │Health    │  │Connection│  │Metrics Collector     │ │
│  │Checker   │  │Pool      │  │                      │ │
│  └──────────┘  └──────────┘  └──────────────────────┘ │
└────────────────────────────────────────────────────────┘
`

### Hash Ring Manager Internals

**Data Structure:**
`java
SortedMap<Long, VirtualNode> ring = new TreeMap<>();

record VirtualNode(String physicalNode, int vnodeIndex, long hash) {}

public String findNode(String key) {
    long keyHash = hashFunction.hash(key);
    SortedMap<Long, VirtualNode> tail = ring.tailMap(keyHash);
    if (tail.isEmpty()) {
        return ring.get(ring.firstKey()).physicalNode();
    }
    return tail.get(tail.firstKey()).physicalNode();
}
`

**Memory Layout:**
- TreeMap: O(log N) for insert/delete/lookup
- N = physical nodes × virtual nodes per physical node
- For 100 physical nodes × 150 virtual nodes = 15,000 entries
- Memory: ~2-3 MB

### Connection Pool Internals

`java
public class NodeConnectionPool {
    private final BlockingQueue<Connection> available;
    private final Set<Connection> active;
    private final int maxSize;
    private final Duration timeout;

    public Connection borrowConnection() throws TimeoutException {
        Connection conn = available.poll(timeout);
        if (conn == null) throw new TimeoutException();
        active.add(conn);
        return conn;
    }

    public void returnConnection(Connection conn) {
        active.remove(conn);
        available.offer(conn);
    }
}
`

### Scatter-Gather Engine Internals

**Execution Model:**
1. Accept query and extract routing keys (if any)
2. If routing keys present: route to specific nodes only
3. If no routing keys: broadcast to ALL nodes
4. Execute queries in parallel using CompletableFuture
5. Collect partial results with timeout
6. Merge results (sort, limit, aggregate)
7. Return consolidated result

**Thread Model (Java 21 virtual threads):**
`java
public CompletableFuture<Result> scatterGather(Query query) {
    var futures = nodes.stream()
        .map(n -> CompletableFuture.supplyAsync(
            () -> executeOnNode(n, query),
            Executors.newVirtualThreadPerTaskExecutor()
        ))
        .toList();

    return CompletableFuture.allOf(futures.toArray(new CompletableFuture[0]))
        .orTimeout(5000, MILLISECONDS)
        .handle((v, ex) -> {
            if (ex != null) return handlePartialFailure(futures);
            return mergeResults(futures);
        });
}
`

### Rebalancing Engine Internals

**Rebalancing Algorithm:**
1. Collect current data distribution
2. Calculate target distribution (even across all nodes)
3. For each node, identify keys that need to move
4. Create migration plan (batched key ranges)
5. Execute migration in parallel with throttling
6. Verify consistency after each batch
7. Update routing table atomically
8. Clean up migrated data from source nodes

**State Machine:**
`
IDLE → ANALYZING → PLANNING → MIGRATING → VERIFYING → UPDATING → CLEANUP → IDLE
                           ↓                        ↑
                        (error) → ROLLING_BACK ─────┘
`

### Monitoring Internals

**Metrics Collected:**
- Per-node: QPS, latency (P50/P99/P999), error rate, data size
- Per-operation: read/write/delete counts
- System: active connections, rebalance progress

**Exposure:**
- JMX MBeans for each node
- Micrometer integration for Prometheus
- Structured JSON logs
