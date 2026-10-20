# How It Works: CockroachDB

## Core Mechanism
CockroachDB works by distributing data and query load across multiple independent database instances. The fundamental insight is that splitting a large problem into smaller parallel pieces is more scalable than solving the entire problem on a single machine.

## Step-by-Step Flow

### Step 1: Key Extraction
When a query arrives, the system extracts the routing key from the query parameters.

Example: SELECT * FROM orders WHERE order_id = 12345 → routing key = 12345

### Step 2: Hash Computation
The routing key is hashed to produce a uniform random value:
`
hash = SHA-256(\"12345\") & 0x7FFFFFFFFFFFFFFF
     = 0x8F3B5A2C1D4E6F78
`

### Step 3: Node Lookup
The hash is used to find the responsible node on the consistent hash ring:
`
ring.lookup(0x8F3B5A2C1D4E6F78) → \"node-03\"
`

### Step 4: Query Routing
The query is forwarded to the determined node's connection pool:
`
connectionPool(\"node-03\").execute(query) → Result
`

### Step 5: Result Return
The result is returned to the client. For cross-node queries, steps 2-4 are repeated for each node, and results are merged.

## Why It Works

### Distribution
Hashing provides mathematically guaranteed uniform distribution across nodes:
`
P(key → node_i) = 1/N for all i
`

### Scalability
Adding more nodes increases total capacity linearly.

### Fault Tolerance
If a node fails, traffic is automatically redirected to remaining nodes (consistent hashing minimizes the impact).

## Key Algorithms

### Consistent Hashing
`
hash_ring = []
for each node in nodes:
    for vnode in 0..V-1:
        hash_ring.add(hash(node + \":vnode:\" + vnode), node)
hash_ring.sort()

def find_node(key):
    h = hash(key)
    idx = binary_search(hash_ring, h)
    return hash_ring[idx].node
`

### Scatter-Gather
`
def scatter_gather(query):
    futures = [async_execute(node, query) for node in all_nodes]
    results = [await f for f in futures]
    return merge(results)
`

## The Math Behind It
Given N nodes and K keys:
- Expected keys per node: K/N
- Variance: K(N-1)/N²
- Standard deviation: âˆš(K(N-1)/N²)

For K=1,000,000 keys and N=10 nodes:
- Expected: 100,000 keys/node
- Std dev: ~300 keys (0.3% variation)

## Implementation Considerations

### Hash Function Selection
- **SHA-256**: Cryptographically secure, good distribution, slower
- **MurmurHash3**: Fast, excellent distribution, not cryptographic
- **FNV-1a**: Very fast, good distribution for short keys

### Virtual Nodes
Without virtual nodes, adding/removing a physical node causes K/N keys to move. With V virtual nodes, movement is more granular.

### Consistency vs. Availability
The system can be tuned for:
- **Strong consistency**: All replicas acknowledge before returning
- **High availability**: Accept writes as long as any replica is available
- **Balanced**: Quorum-based writes (W + R > N)

## Real-World Behavior

### Under Normal Conditions
- P50 latency: 1-5ms
- P99 latency: 10-50ms
- Throughput: 10,000-100,000 ops/sec

### Under Stress
- P50: 5-20ms
- P99: 100-500ms
- Throughput degrades gracefully (no cliff)
