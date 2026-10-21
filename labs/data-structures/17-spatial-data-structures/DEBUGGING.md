# Debugging Spatial Data Structures

## Common Issues
| Symptom | Cause |
|---------|-------|
| Point not found | Wrong boundary check |
| Too many subdivision levels | Capacity too small |
| Nearest neighbor wrong | Pruning not aggressive enough |
| Range search misses points | Intersection calculation error |
| Stack overflow | Deep recursion without limit |
