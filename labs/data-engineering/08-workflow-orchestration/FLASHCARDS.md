# Workflow Orchestration Flashcards

## Card 1
**Front**: What is a DAG in workflow orchestration?
**Back**: Directed Acyclic Graph - a collection of tasks with dependencies arranged in a non-cyclic structure.

## Card 2
**Front**: What is the difference between the Airflow scheduler and executor?
**Back**: Scheduler parses DAGs and determines what to run. Executor runs the actual tasks.

## Card 3
**Front**: What is a sensor in Airflow?
**Back**: An operator that waits for a certain condition (file arrival, database record, API response).

## Card 4
**Front**: What is backfill in Airflow?
**Back**: Running a DAG for historical intervals that were missed, using the start_date and catchup parameter.

## Card 5
**Front**: What is an SLA in Airflow?
**Back**: Service Level Agreement - a time-based commitment for DAG completion, with alerts on miss.
