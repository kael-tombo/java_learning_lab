# Code Deep Dive — Distributed Scheduling

## 1. DistributedScheduler Interface

`java
public interface DistributedScheduler {
    void schedule(Job job, Trigger trigger);
    boolean unschedule(String jobId);
    List<Job> getScheduledJobs();
    boolean isRunning(String jobId);
}
`

## 2. CronExpression Implementation

- Parses standard 5-field cron expression
- Computes next fire time given current time
- Handles special characters: *, /, -, L, W, #
- Pre-computes valid values for each field

## 3. QuartzClusterManager Implementation

- JDBC JobStore with MySQL/PostgreSQL
- Database-level locking for cluster coordination
- Misfire handling (fire now or ignore)
- Job recovery after node failure

## 4. LeaderElectionJob Implementation

- Uses ZooKeeper or database for leader election
- Leader runs the job, followers wait
- On leader failure, new leader takes over
- Fencing tokens to prevent double execution

## 5. PartitionedJobExecutor Implementation

- Jobs assigned to nodes via consistent hash
- Node joins: take ownership of new partitions
- Node leaves: redistribute partitions
- Minimum disruption on topology change
