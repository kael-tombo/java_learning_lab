# Flashcards — Binary Tree Serialization

- Q: Serialization vs deserialization? → A: Tree→String vs String→Tree
- Q: BFS serialization format? → A: Level-order with "null" markers: "1,2,3,null,null,4,5"
- Q: DFS serialization format? → A: Pre-order with "null" markers: "1,2,null,null,3,4,null,null,5,null,null"
- Q: Why null markers? → A: Preserve structure — distinguish different shapes with same values
- Q: BFS time/space? → A: O(n) both — visit each node once, queue + string O(n)
- Q: DFS time/space? → A: O(n) both — recursion stack O(h) ≤ O(n)
- Q: BFS deserializer queue usage? → A: Holds parents waiting for children; poll parent, assign next 2 values as left/right
- Q: BFS vs DFS advantages? → A: BFS: natural for complete trees, level-by-level. DFS: compact for skewed, simpler recursion
- Q: Empty tree serialization? → A: "" (empty string) in both approaches
- Q: BFS enqueue null children? → A: Yes — maintains position info, written as "null" when dequeued
- Q: Pre-order traversal order? → A: Root, Left, Right
- Q: How does DFS deserializer know structure? → A: Null markers explicitly mark missing children; recursion follows pre-order
- Q: Trailing comma handling? → A: split(",") produces empty string; bounds check prevents access
- Q: N-ary tree serialization? → A: Include child count or use delimiter; DFS: count then children; BFS: count or null separator
- Q: Codec class name? → A: Standard name for serializer/deserializer pair