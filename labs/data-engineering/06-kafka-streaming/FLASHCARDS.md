# Kafka Streams Flashcards

## Card 1
**Front**: What is a KStream?
**Back**: An append-only stream of records where each record is an independent fact.

## Card 2
**Front**: What is a KTable?
**Back**: A changelog stream where each record represents an update/upsert to a key.

## Card 3
**Front**: What is the stream-table duality?
**Back**: A stream can be viewed as a table (current state), and a table can be viewed as a stream (changelog).

## Card 4
**Front**: What is a state store in Kafka Streams?
**Back**: Local embedded storage (RocksDB) for stateful operations like aggregations and joins.

## Card 5
**Front**: What is interactive queries?
**Back**: Ability to query Kafka Streams' state stores directly via API, enabling read-your-writes consistency.
