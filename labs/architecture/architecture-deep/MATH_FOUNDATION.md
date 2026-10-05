# Math Foundation — Architecture Deep Dive

## Queueing Theory

### Little's Law

**Formula:** L = λ × W

Where:
- L = Average number of items in the system
- λ = Average arrival rate of items
- W = Average time an item spends in the system

**Application:** If a service receives 1000 requests/second and each
request takes 50ms to process, the average number of concurrent requests
is L = 1000 × 0.05 = 50.

### Utilization and Queueing

**Formula:** Wq = ρ / (μ × (1 - ρ))

Where:
- Wq = Average waiting time in queue
- ρ = Utilization (λ/μ)
- μ = Service rate

**Key insight:** As utilization approaches 100%, waiting time increases
dramatically. At 90% utilization, waiting time is 9x the service time;
at 99%, it's 99x.

## Probability and Statistics

### Availability Calculations

**Formula:** Availability = MTBF / (MTBF + MTTR)

Where:
- MTBF = Mean Time Between Failures
- MTTR = Mean Time To Recovery

**Example:** If MTBF = 1000 hours and MTTR = 1 hour:
Availability = 1000 / 1001 = 99.9%

### Nines of Availability

| Availability | Downtime per year | Downtime per month |
|-------------|-------------------|-------------------|
| 99% | 3.65 days | 7.3 hours |
| 99.9% | 8.76 hours | 43.8 minutes |
| 99.99% | 52.6 minutes | 4.38 minutes |
| 99.999% | 5.26 minutes | 26.3 seconds |

### Series and Parallel Systems

**Series:** All components must work.
Availability = A1 × A2 × A3 × ... × An

**Parallel:** At least one component must work.
Availability = 1 - (1 - A1) × (1 - A2) × ... × (1 - An)

**Example:** Two services in series, each 99.9% available:
Availability = 0.999 × 0.999 = 99.8%

Two services in parallel, each 99.9% available:
Availability = 1 - (0.001 × 0.001) = 99.9999%

## Capacity Planning

### Throughput Calculation

**Formula:** Throughput = Concurrency / Response Time

**Example:** If a service handles 100 concurrent requests with 200ms
response time: Throughput = 100 / 0.2 = 500 requests/second.

### Little's Law for Capacity

**Formula:** Required Concurrency = Throughput × Response Time

**Example:** To handle 1000 requests/second with 100ms response time:
Required Concurrency = 1000 × 0.1 = 100 concurrent connections.

## Consistency and Coordination

### Quorum Systems

**Formula:** W + R > N

Where:
- N = Total number of replicas
- W = Write quorum (number of nodes that must acknowledge write)
- R = Read quorum (number of nodes that must respond to read)

**Example:** With N=5, W=3, R=3: 3 + 3 > 5, so reads and writes overlap,
ensuring read-your-writes consistency.

### CAP Theorem Implications

**Partition probability:** In practice, network partitions are rare but
inevitable. The choice is between:
- **CP systems**: Sacrifice availability during partitions (e.g., ZooKeeper)
- **AP systems**: Sacrifice consistency during partitions (e.g., Cassandra)

## Performance Modeling

### Amdahl's Law

**Formula:** Speedup = 1 / ((1 - P) + P/S)

Where:
- P = Fraction of program that can be parallelized
- S = Speedup of the parallel portion

**Example:** If 60% of a system can be parallelized with 4x speedup:
Speedup = 1 / (0.4 + 0.6/4) = 1 / 0.55 = 1.82x

### Universal Scalability Law

**Formula:** C(N) = N / (1 + σ(N-1) + κN(N-1))

Where:
- C(N) = Capacity with N nodes
- N = Number of nodes
- σ = Contention parameter (serialization)
- κ = Crosstalk parameter (communication overhead)

## Reliability Engineering

### Error Budgets

**Formula:** Error Budget = (1 - SLO) × Time Period

**Example:** For 99.9% SLO over 30 days:
Error Budget = 0.001 × 30 days = 43.2 minutes of allowed downtime

### Failure Rate and Redundancy

**Formula:** System Failure Rate = λ1 × λ2 × ... × λn × MTTR

**Example:** Two redundant components, each with failure rate 0.001/hour
and MTTR of 1 hour:
System Failure Rate = 0.001 × 0.001 × 1 = 0.000001/hour

## Cost Modeling

### Total Cost of Ownership (TCO)

**Formula:** TCO = Infrastructure + Operations + Development + Downtime Cost

**Key factors:**
- Infrastructure: Compute, storage, networking
- Operations: Monitoring, maintenance, incident response
- Development: Feature development, bug fixes
- Downtime: Lost revenue, reputation damage

### Cost per Request

**Formula:** Cost per Request = Total Cost / Total Requests

**Example:** If monthly cost is $10,000 and 10M requests:
Cost per Request = $10,000 / 10,000,000 = $0.001

## Consistency Models and Latency

### Eventual Consistency Convergence

**Formula:** Convergence Time ≈ Replication Lag + Conflict Resolution Time

**Key factors:**
- Network latency between nodes
- Replication frequency
- Conflict detection and resolution overhead

### Read-Your-Writes Guarantee

**Implementation:** Route reads to the same node that handled the write,
or use version vectors to ensure the read reflects the write.
