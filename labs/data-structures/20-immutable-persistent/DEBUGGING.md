# Debugging

## Common Issues
| Symptom | Cause |
|---------|-------|
| Mutation visible in old version | Accidental mutable reference |
| Stack overflow | Deep recursion without tail-call |
| Memory exhaustion | Not sharing structure properly |
| Wrong equals/hashCode | Value comparison not implemented |
| Unexpected thread interference | Object not truly immutable |
