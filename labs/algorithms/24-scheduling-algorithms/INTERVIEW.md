# Interview Questions: Scheduling Algorithms

## LeetCode Problem Map
| Problem | Difficulty | Company Signal | Pattern |
|---------|-----------|----------------|---------|
| LC 621 Task Scheduler | Medium | Google, Meta, Microsoft | Greedy / idle calculation |
| LC 630 Course Schedule III | Hard | Google, Amazon | Max-heap + sorting |
| LC 1353 Maximum Meetings | Medium | Google, Amazon | Greedy by end time |
| LC 207 Course Schedule | Medium | Google, Meta, Amazon | Topological sort |
| LC 210 Course Schedule II | Medium | Google, Meta, Amazon | Topological sort |
| LC 1834 Single-Threaded CPU | Medium | Google, Amazon | Min-heap + sorting |
| LC 1882 Process Tasks Using Servers | Medium | Google | Two heaps |

## NeetCode Reference
- LC 207 Course Schedule (NeetCode 150)
- LC 210 Course Schedule II (NeetCode 150)
- LC 621 Task Scheduler (NeetCode 150)

## Company-Specific Questions
### Google
- Design a job scheduler for Google Cloud Tasks with priority queues
- How would you schedule MapReduce tasks across a cluster?
- Implement a DAG-based scheduler similar to Apache Airflow

### Microsoft
- How does Windows NT Kernel schedule threads (priority + quantum)?
- Design a scheduler for Azure Batch compute jobs
- Explain the SQL Server query scheduler and resource governor

### Meta
- Design a scheduler for Facebook's news feed ranking pipeline
- How would you schedule background jobs for photo processing?
- Implement a delayed job processing system for notifications

### Amazon
- Design a scheduler for AWS Lambda invocations with cold start mitigation
- How does Fargate schedule containers across the cluster?
- Implement a priority queue for Amazon order fulfillment pipeline

### Apple
- Design a power-efficient task scheduler for iOS background tasks
- How does Grand Central Dispatch (GCD) schedule work on multicore?
- Implement a scheduler for Time Machine backup jobs with rate limiting

### Oracle
- Design a job scheduler for Oracle Enterprise Scheduler
- How does Oracle Database Resource Manager allocate CPU?
- Implement a cron-style scheduler for database maintenance windows

## Real Production Scenarios
- Scenario 1: Airflow DAG scheduler - optimizing task dependencies and retry logic for a data pipeline processing 10TB nightly with SLA constraints
- Scenario 2: Kubernetes batch job scheduling - configuring resource requests, limits, and priority classes for a Spark cluster
- Scenario 3: Debugging scheduler starvation - a low-priority batch job never gets CPU because higher-priority jobs keep arriving, requiring priority aging

## Interview Tips
- Understand FCFS, SJF, Priority, Round Robin, and Multilevel Feedback Queue
- Know how to compute metrics: turnaround time, waiting time, response time
- Greedy + heap is the most common LC pattern for scheduling problems
- Common edge cases: zero-length tasks, simultaneous arrivals, preemption vs non-preemption

## Java-Specific Considerations
- java.util.PriorityQueue is the primary data structure for scheduling simulations
- ScheduledExecutorService for real Java scheduling (with scheduleAtFixedRate and scheduleWithFixedDelay)
- Delayed interface and DelayQueue for scheduling with deadline semantics
- Pitfall: comparing tasks by start time then end time in heaps (tie-breaking matters)
- Pitfall: long-running tasks blocking the scheduler loop; use CompletableFuture for async dispatch
- For topological scheduling: Kahn's algorithm with Queue<Integer> for order of execution
