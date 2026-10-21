# Refactoring — Distributed ID Generation

1. Extract IdGenerator interface for pluggable implementations
2. Separate timestamp source from generator logic
3. Use builder pattern for Snowflake configuration
4. Extract encoding/decoding into utility classes
5. Add metrics wrapping for monitoring
6. Use strategy pattern for collision resolution
7. Separate worker ID allocation from generation
