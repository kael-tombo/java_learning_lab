# Common Mistakes with Skip Lists

1. **Incorrect level generation**: Using wrong probability or MAX_LEVEL
2. **Not using sentinel header**: Complicates edge cases
3. **Wrong update array initialization**: Must start from header
4. **Memory leaks**: Not properly removing nodes on delete
5. **Duplicate keys**: Need consistent handling strategy
6. **Integer overflow in level calculation**: For very large n
7. **Dangling pointers**: Not updating all levels on insert/delete
