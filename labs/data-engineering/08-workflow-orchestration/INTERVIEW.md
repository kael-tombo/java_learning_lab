# Workflow Orchestration Interview Questions

## Beginner
**Q**: What is a DAG and why must it be acyclic?
**A**: A Directed Acyclic Graph defines task dependencies. It must be acyclic because cycles would create infinite execution loops.

## Intermediate
**Q**: How would you handle task failures in Airflow?
**A**: Configure retries (count and delay), retry exponential backoff, SLA alarms, email/slack alerts, and dead letter queues for unrecoverable failures.

## Advanced
**Q**: Design a multi-team Airflow deployment.
**A**: Use namespaced DAG folders per team, RBAC for access control, pool-based resource management, and separate environments (dev/staging/prod) with CI/CD pipeline.
