# CDC Flashcards

## Card 1
**Front**: What is Change Data Capture?
**Back**: A pattern for tracking and capturing database changes (inserts, updates, deletes) in real-time.

## Card 2
**Front**: What are the three CDC mechanisms?
**Back**: Log-based (binlog/WAL), trigger-based, and query-based (timestamp columns).

## Card 3
**Front**: What is Debezium?
**Back**: An open-source CDC platform that uses Kafka Connect to stream database changes to Kafka.

## Card 4
**Front**: What is the outbox pattern?
**Back**: Applications write explicit events to an outbox table, which CDC captures for reliable event publishing.

## Card 5
**Front**: What is a snapshot in CDC?
**Back**: An initial read of all existing data in a table before streaming begins.
