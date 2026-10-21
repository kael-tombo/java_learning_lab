# 19 - Distributed Scheduling

## Overview
Distributed scheduling coordinates time-based and event-driven job execution across multiple nodes. This lab covers Quartz Scheduler, distributed cron, leader election for job execution, and job partitioning.

## Prerequisites
- Java 21+
- Maven 3.8+
- Understanding of distributed systems
- Familiarity with cron and scheduling concepts

## Topics Covered
- Quartz Scheduler architecture and clustering
- Distributed cron with leader election
- Job partitioning and sharding
- Exactly-once job execution guarantees
- Scheduler failover and recovery
- Dynamic job scheduling
- Cron expression parsing and evaluation

## Package Structure
- com.distributed.scheduling — Core implementations
  - DistributedScheduler.java — Scheduler interface
  - CronExpression.java — Cron parser
  - QuartzClusterManager.java — Quartz cluster support
  - LeaderElectionJob.java — Leader-based job execution
  - PartitionedJobExecutor.java — Sharded job execution
  - JobStore.java — Persistent job storage
