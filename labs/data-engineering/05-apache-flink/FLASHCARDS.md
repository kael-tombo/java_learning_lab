# Apache Flink Flashcards

## Card 1
**Front**: What is event time in Flink?
**Back**: The time when an event actually occurred, embedded in the event data itself.

## Card 2
**Front**: What is a watermark?
**Back**: A signal that indicates no events with timestamp less than the watermark value will arrive.

## Card 3
**Front**: What is managed state in Flink?
**Back**: State automatically managed by Flink, with checkpointing and recovery support.

## Card 4
**Front**: What are the three types of windows in Flink?
**Back**: Tumbling (fixed non-overlapping), Sliding (fixed overlapping), Session (based on inactivity gaps).

## Card 5
**Front**: What is the difference between savepoints and checkpoints?
**Back**: Savepoints are manually triggered for planned upgrades; checkpoints are automatic for fault tolerance.
