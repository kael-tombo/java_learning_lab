# Code Deep Dive — Distributed Filesystems

## 1. DistributedFileSystem Interface

`java
public interface DistributedFileSystem {
    void write(String path, InputStream data);
    InputStream read(String path);
    boolean delete(String path);
    List<FileInfo> list(String path);
    long getSize(String path);
}
`

## 2. ErasureCodec Implementation

Reed-Solomon encoding:
1. Split data into k equal-sized fragments
2. Compute m parity fragments using Vandermonde matrix
3. Store fragments across k+m nodes
4. Reconstruct from any k fragments using matrix inversion

## 3. FileReplicator Implementation

- Watches for node failures
- Triggers re-replication of blocks on failed nodes
- Maintains target replication factor
- Balances replicas across nodes and racks

## 4. MetadataStore Implementation

- Caches file-to-block mappings
- Persists metadata to database or consensus store
- Handles concurrent mutations with optimistic locking
- Provides atomic rename and directory operations
