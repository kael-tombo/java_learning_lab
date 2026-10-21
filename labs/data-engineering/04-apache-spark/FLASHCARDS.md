# Apache Spark Flashcards

## Card 1
**Front**: What is Apache Spark?
**Back**: Unified analytics engine for large-scale data processing with built-in modules for SQL, streaming, ML, and graph processing.

## Card 2
**Front**: What is an RDD?
**Back**: Resilient Distributed Dataset - immutable, partitioned collection that can be operated in parallel with automatic fault recovery.

## Card 3
**Front**: What is lazy evaluation in Spark?
**Back**: Transformations are not executed until an action is called, allowing Spark to optimize the execution plan.

## Card 4
**Front**: What is the Catalyst Optimizer?
**Back**: Spark SQL's query optimizer that transforms logical plans into efficient physical plans using rule and cost-based optimization.

## Card 5
**Front**: What is a shuffle in Spark?
**Back**: A redistribution of data across partitions, required for wide dependencies like groupBy or join, and is the most expensive operation.
