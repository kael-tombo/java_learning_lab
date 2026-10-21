# Interview: CQRS Axon

Q: What is CQRS? A: Separating command (write) and query (read) responsibilities into different models.

Q: What is event sourcing? A: Storing all changes as a sequence of events instead of current state.

Q: What is a saga? A: A sequence of steps in a distributed transaction, guaranteed to complete or compensate.

Q: When to use CQRS? A: When read and write patterns have different requirements, or when audit trail is critical.
