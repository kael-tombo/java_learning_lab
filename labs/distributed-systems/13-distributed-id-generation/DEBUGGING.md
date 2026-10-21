# Debugging — Distributed ID Generation

## Common Issues
1. Duplicate IDs: Check clock rollback handling
2. Non-monotonic IDs: Verify sequence logic
3. Slow generation: Check SecureRandom performance
4. Worker ID conflicts: Verify allocation mechanism

## Debugging Techniques
- Enable trace logging for ID generation
- Monitor sequence utilization per millisecond
- Validate monotonicity in tests
- Check worker ID uniqueness at startup
