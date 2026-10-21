# Architecture of Skip Lists

## Integration Patterns

Skip lists serve as:
- Backing data structure for ordered maps/sets
- Index structure for in-memory databases
- Priority queue implementation
- Concurrent sorted data structure

## Design Decisions

1. **MAX_LEVEL selection**: 32 for general use, adjust for specific n
2. **Probability p**: 0.5 is standard, 0.25 for less memory but more levels
3. **Sentinel header**: Simplifies code but adds memory overhead
4. **Random vs deterministic**: Skip lists are probabilistic by nature
