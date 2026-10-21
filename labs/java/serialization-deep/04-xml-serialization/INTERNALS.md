# XML Serialization -- Internal Implementation

## Internal Architecture

### Core Data Structures

#### 1. Handle Table
The handle table maps serialized objects to unique integer handles.
- Array-based implementation for O(1) lookups
- Grows dynamically as new objects are encountered
- Reset between serialization sessions
- Supports circular reference detection

#### 2. Class Descriptor Cache
Class metadata is cached to avoid redundant reflection:
- Keyed by Class object for fast lookup
- Stores Field[], Method[], and annotation data
- Thread-safe concurrent access via ConcurrentHashMap
- Lazy population on first use of each class

#### 3. Serializer Registry
Mapping from Class to Serializer instance:
- Registration order determines serialization IDs
- Built-in serializers for common types (primitives, String, arrays)
- Custom serializers can override defaults
- Thread-safe for concurrent reads, locked for writes

### Internal Algorithms

#### Object Graph Traversal
1. Start at root object and check handle table
2. If new, assign handle and write class descriptor
3. Recursively serialize all referenced fields
4. Handle circular references via handle table lookup
5. Continue until all reachable objects are serialized

#### Type Resolution
1. Check registered serializers first (fast path)
2. Fall back to reflective serialization (slow path)
3. Cache resolved serializer for future use
4. Handle polymorphic types via type registration

### Memory Management

#### Buffer Pooling
- Pre-allocated buffer pools reduce GC pressure
- Configurable minimum and maximum buffer sizes
- Automatic buffer growth with doubling strategy
- Buffer reuse across serialization operations

#### Object Allocation
- Objects allocated without constructor invocation
- Uses Unsafe.allocateInstance for direct allocation
- Fields populated via reflection or Unsafe.putX
- Final fields handled specially (may be cleared by JVM)

### Thread Safety Mechanisms
- ThreadLocal caching of Kryo instances avoids synchronization
- ObjectOutputStream/InputStream methods are synchronized
- Pool-based recycling for controlled thread safety
- ConcurrentHashMap for caches with concurrent read access

### Performance Optimizations
- Intrusive caching of serializer instances by type
- Field metadata cached per class on first access
- String interning for class names reduces duplicate storage
- Thread-local buffers for temporary data avoids allocation
- Bulk writes for primitive arrays reduce method call overhead
