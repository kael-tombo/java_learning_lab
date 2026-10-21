# Mental Models for Kafka Streaming

## 1. The Whiteboard
- **KStream** = Dry-erase marker (writes facts, permanent)
- **KTable** = Pencil (writes current state, can erase/update)
- **State Store** = Sticky notes (local state for fast access)

## 2. The Ledger
- **KStream** = Journal entries (every transaction recorded)
- **KTable** = Account balance (current state derived from journal)
- **State store** = Running tally maintained by accountant

## 3. The Messaging App
- **KStream** = Chat messages flowing by (each message is independent)
- **KTable** = Contact list (latest info about each person)
- **State store** = Local cache of contacts on your phone
