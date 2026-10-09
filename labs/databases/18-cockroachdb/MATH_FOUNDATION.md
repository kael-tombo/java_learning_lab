# Math Foundation: CockroachDB

## Mathematical Models and Formulas

### 1. Probability Theory

#### 1.1 Uniform Distribution
For N items distributed across M shards with ideal uniform hashing:
- E[items_per_shard] = N/M
- Var[items_per_shard] = N(M-1)/M^2

The probability that a specific shard receives exactly k items follows a binomial distribution.

#### 1.2 Hash Collision Probability (Birthday Problem)
Given N keys and H hash values, probability of at least one collision:
P ≈ 1 - e^(-N(N-1)/(2H))

For N=10^6, H=2^64: P ≈ 2.7 × 10^-8

#### 1.3 Load Balancing Metrics
Skew Factor: skew = max_load / avg_load - 1
Entropy: H = -Σ p_i log₂(p_i)
For perfect distribution: H = log₂(n)

### 2. Consistent Hashing

#### 2.1 Ring Distance
On a hash ring of size R: distance(a,b) = (b-a+R) mod R

#### 2.2 Expected Migration on Node Change
Adding one node to N existing nodes:
- With consistent hashing: fraction 1/(N+1) keys move
- With modulo hashing: fraction N/(N+1) keys move

#### 2.3 Virtual Node Distribution
With V virtual nodes per physical node, N physical nodes, K total keys:
- E[keys_per_physical] = K/N
- σ ≈ √(K(1-1/(NV))/(NV))

### 3. Performance Modeling

#### 3.1 Amdahl's Law for Parallel Queries
Speedup = 1 / ((1-P) + P/N)
Where P = parallelizable fraction, N = number of nodes

#### 3.2 Query Latency Model
T_total = T_network + T_queue + T_service
For scatter-gather queries:
T_sg = max_i(T_network_i + T_queue_i + T_service_i) + T_merge

### 4. Queueing Theory

#### 4.1 M/M/1 Queue
For a single server with Poisson arrivals and exponential service:
L = λ / (μ - λ)  (average number in system)
W = 1 / (μ - λ)  (average time in system)

#### 4.2 Little's Law
L = λ × W
Number of items in system = arrival rate × average time in system.

### 5. Computational Complexity

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|-----------------|
| Hash computation | O(k) key length | O(1) |
| Consistent hash lookup | O(log VN) | O(VN) |
| Scatter-gather merge | O(R log R) | O(R) |
| Rebalancing | O(K) keys to move | O(1) per key |

### 6. Capacity Planning Formulas

#### 6.1 Storage per Shard
storage_per_shard = (total_data + growth × days) / num_shards + overhead

#### 6.2 Query Throughput
max_queries = num_shards × queries_per_shard_per_second

#### 6.3 Rebalancing Time
rebalance_time = data_to_move / network_bandwidth + overhead

### 7. Statistical Tests

#### Chi-squared Test for Distribution Uniformity
χ² = Σ (O_i - E_i)² / E_i
Null hypothesis: data is uniformly distributed. Reject if χ² > χ²_critical.

#### Kolmogorov-Smirnov Test
For comparing distributions before and after rebalancing.
