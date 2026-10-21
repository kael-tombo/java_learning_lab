# Mental Models for Orchestration

## 1. The Construction Project
- **Tasks** = Construction activities (pour foundation, frame walls)
- **Dependencies** = Order of work (foundation before walls)
- **DAG** = Construction schedule
- **Scheduler** = Project manager
- **Retry** = Fix and redo failed work

## 2. The Recipe
- **Steps** = Recipe instructions
- **Dependencies** = Step order (marinate before cooking)
- **Parallel steps** = Chop vegetables while sauce simmers
- **Failure** = Burned dish, start over or salvage

## 3. The Factory Production Line
- **DAG** = Assembly line design
- **Tasks** = Workstations
- **Dependencies** = Conveyor belt direction
- **Sensors** = Quality check stations
- **Backfill** = Catch up production after shutdown
