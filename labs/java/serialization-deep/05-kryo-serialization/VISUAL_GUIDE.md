# Kryo Serialization -- Visual Guide

## Architecture Diagram

The serialization architecture follows a layered pipeline pattern:

+------------------+     +------------------+
|   Java Object    | --> | Serialization    |
| (Object Graph)   |     |    Engine        |
+------------------+     +--------+---------+
                                  |
                        +--------+---------+
                        |    Stream Writer  |
                        +--------+---------+
                                  |
                        +--------+---------+
                        |    Output Stream  |
                        | (File, Network,   |
                        |  ByteArray)       |
                        +------------------+

## Object Graph Serialization Flow

The traversal is depth-first with handle-based reference tracking:

Root Object --> Field 1 (primitive) --> Write directly
             --> Field 2 (String) --> Write UTF
             --> Field 3 (Reference) --> Check handle table
                     --> New object --> Assign handle, serialize
                     --> Existing --> Write handle reference
             --> Field 4 (Array) --> Write length + elements
             --> Field 5 (Collection) --> Write size + elements

## Stream Format Layout

+------------------+
| Magic (0xACED)   | 2 bytes
+------------------+
| Version (0x0005) | 2 bytes
+------------------+
| Class Desc       | Variable
| - Class Name     | UTF string
| - serialVersionUID | 8 bytes
| - Field Count    | 2 bytes
| - Fields         | Variable
+------------------+
| Object Data      | Variable
+------------------+
| TC_ENDBLOCKDATA  | 1 byte
+------------------+

## Thread Safety Architecture

Thread 1 --> Kryo Instance 1 (exclusive)
Thread 2 --> Kryo Instance 2 (exclusive)
Thread 3 --> Kryo Instance 3 (exclusive)
                |
          +-----+------+
          |  Kryo Pool |
          +-----+------+
                |
          Borrow/Release

## Data Flow Diagram

Serialization: Object -> Introspect Fields -> Encode -> Write Stream
Deserialization: Read Stream -> Decode -> Allocate Object -> Populate Fields

## Memory Layout During Serialization

Heap: Object Graph + Handle Table + Class Descriptors + Output Buffer
Stack: Recursion Depth (max nesting level)
Off-Heap: DirectByteBuffer (if using NIO)
