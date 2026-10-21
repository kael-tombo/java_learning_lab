# Debugging

## Common Issues
| Symptom | Cause |
|---------|-------|
| Wrong element returned | Head not advanced correctly |
| Buffer reports wrong size | Size not updated atomically |
| Null pointer on poll | Empty buffer not checked |
| Elements lost | Overwrite when should block |
| Thread hangs | Deadlock on condition variables |
