# Mental Models for Flink

## 1. The Factory Conveyor Belt
- **Source** = Products enter belt
- **Operators** = Workstations along belt
- **State** = Tools/materials at each station
- **Checkpoints** = Photos of assembly line state
- **Watermarks** = Clock showing time progress

## 2. The Theme Park Queue
- **Rides** = Operators
- **Queue lines** = Buffers
- **Fast passes** = Watermarks
- **Photo snapshots** = Checkpoints
- **Ride groups** = Keyed streams

## 3. The Newspaper Production
- **Events** = News stories arriving
- **Event time** = When story happened
- **Processing time** = When story is printed
- **Watermark** = "We've received all stories up to 5pm"
- **Late data** = Tomorrow's corrections page
