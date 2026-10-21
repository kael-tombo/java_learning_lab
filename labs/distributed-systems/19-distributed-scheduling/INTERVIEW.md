# Distributed Scheduling - Interview Preparation

> Key interview questions about distributed job scheduling and resource management.

---

## Core Interview Questions

### Q1: How does Google's Borg scheduler work?
**Answer**: Borg: cluster management system at Google. Jobs submitted to BorgMaster (Paxos-replicated). Borglet agent on each machine. Scheduling: feasibility checking (resource requirements) -> scoring (best fit). Admission control, resource estimation, preemption for high-priority jobs. Cell concept for fault isolation.

### Q2: Compare Borg vs Kubernetes scheduling
**Answer**: Kubernetes: open-source Borg-like system. Scheduler uses predicates (filters) and priorities (scoring). Pod requests resources (CPU, memory, GPU). Scheduler binds pod to node. K8s scheduler is pluggable; can be replaced (e.g., Spark K8s scheduler). Borg has richer resource estimation (dynamic).

### Q3: What is the "bin packing" problem in distributed scheduling?
**Answer**: Efficiently placing jobs/tasks onto machines to maximize utilization. Form of NP-hard vector bin packing. Heuristics: first-fit decreasing, best-fit decreasing. Kubernetes uses binpacking scoring: prefer nodes with highest resource utilization after placing pod.

### Q4: How do you handle priority and preemption in scheduling?
**Answer**: Priority classes (non-preempting, preempting). Preemption: lower-priority pods evicted to make room for higher-priority. Kubernetes: PriorityClass with value; scheduler can preempt lower-priority pods. Proportional set size (PSS) for fair scheduling. Gang scheduling for batch jobs.

### Q5: How does distributed cron/task scheduling work?
**Answer**: Distributed cron: timetable stored in ZooKeeper/etcd. Leader elects to process schedule. Tasks distributed via task queue. Each task idempotent (with dedup). Cron triggers scheduled task -> task queued -> worker picks up. Job history tracked in database.

## Company-Specific Focus

| Company | Scheduling Focus |
|---------|-----------------|
| Google | "Borg, Omega, Kubernetes scheduling evolution" |
| Apache | "Spark dynamic resource allocation" |
| Hashicorp | "Nomad batch scheduling" |
| Microsoft | "Azure Batch scheduling" |

## LeetCode Connections

| Problem | # | Scheduling Concept |
|---------|---|-------------------|
| Task Scheduler | 621 | CPU scheduling |
| Meeting Rooms II | 253 | Resource scheduling |
| Maximum Profit in Job Scheduling | 1235 | Job scheduling optimization |
| Minimum Number of Refueling Stops | 871 | Resource-aware scheduling |
| Course Schedule III | 630 | Deadline-aware scheduling |

## System Design Connections

- **Design a Job Scheduler**: Priority queue with worker pools
- **Design a Cron-like Service**: Distributed timer + task queue
- **Design a Cluster Scheduler**: Resource-aware task placement
- **Design a Stream Processing Framework**: Schedule tasks across partitions

> **Key Insight**: Scheduling interviews test your understanding of resource constraints, priority handling, and the tradeoff between utilization and fairness.