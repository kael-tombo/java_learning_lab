# Mental Models: CockroachDB

## 1. The Library Analogy
Imagine a massive library with millions of books. Instead of one giant building, we have multiple branch libraries.
- **Nodes**: Each branch library holds a subset of the books
- **Routing key**: The call number determines which branch has a book
- **Router**: The library catalog tells you which branch to go to
- **Cross-node query**: Searching by author (not call number) requires checking all branches
- **Rebalancing**: Moving books between branches when a new branch opens

## 2. The Pizza Analogy
A large pizza needs to be shared among many people. Slicing makes it manageable.
- **Data**: The whole pizza
- **Nodes**: Individual slices
- **Routing key**: Which slice a topping ends up on
- **Even distribution**: A good pizza cutter makes equal slices
- **Hotspot**: A slice with extra toppings gets eaten faster

## 3. The City Districts Analogy
A growing city divides into districts for efficient governance.
- **City**: The entire dataset
- **Districts**: Database nodes
- **Address**: The routing key (determines which district)
- **City services**: Cross-node queries (more complex)
- **District mayor**: Primary database for the node

## 4. The Bucket Brigade
Water needs to be carried across a field. One person can't carry enough.
- **Water**: Data to be processed
- **People in line**: Database nodes
- **Each bucket**: A unit of work (query)
- **Brigade captain**: The router (directs where each bucket goes)

## 5. The Filing Cabinet Model
A company's records grow beyond one filing cabinet.
- **Multiple cabinets**: Nodes
- **Labels**: Routing key
- **File clerk**: Router (knows which cabinet has which files)
- **Cross-reference index**: Cross-node query capability
- **New cabinet**: Adding a node

## 6. The Restaurant Kitchen Analogy
A busy restaurant kitchen divides tasks among stations.
- **Stations**: Nodes (salad station, grill station, dessert station)
- **Ticket**: Query with routing key (which station to send to)
- **Chef de partie**: Primary database for that station
- **Expediter**: Router (reads tickets, assigns to stations)

## Key Takeaways
1. Partitioning is natural: Dividing work is a universal pattern for handling scale
2. Routing is critical: Knowing where to find things is the key challenge
3. Parallelism improves throughput: Multiple workers are faster than one
4. Cross-partition operations are expensive: Coordinating across partitions adds overhead
5. Plan for growth: Adding capacity should be a designed-in feature
6. Balance is important: Uneven distribution creates bottlenecks
7. Trade-offs everywhere: Every design choice involves compromise
