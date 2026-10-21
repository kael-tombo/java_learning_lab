# Debugging

## Common Issues
| Symptom | Cause |
|---------|-------|
| Wrong min/max for ranges | Incorrect 2^j bounds in DP |
| ArrayIndexOutOfBounds | n - 2^j calculation off |
| Slow query | Not using precomputed log table |
| Wrong for overlapping intervals | Using sum operation (not idempotent) |
