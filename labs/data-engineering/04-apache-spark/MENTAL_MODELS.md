# Mental Models for Spark

## 1. The Kitchen Brigade
- **Driver** = Head chef (plans the menu, coordinates)
- **Executors** = Line cooks (execute tasks)
- **Partitions** = Prep stations (organized work areas)
- **Shuffle** = Passing ingredients between stations

## 2. The Assembly Line
- **Source** = Raw materials at start
- **Transformations** = Workstations along the line
- **Actions** = Completed product at end
- **Lazy Evaluation** = Work only happens when product demanded

## 3. The DAG as Blueprint
- Linear stages connected by dependencies
- Shuffle = Reorganizing between stages
- Narrow dependencies = No reorganization needed
- Wide dependencies = Full reorganization

## 4. The LEGO Model
- RDDs = Individual bricks
- Transformations = Connecting bricks
- Actions = The completed model
- Lineage = Instructions to rebuild
- Persistence = Glue to keep assembled
