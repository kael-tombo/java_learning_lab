# XML Serialization -- How It Works

## Detailed Mechanical Explanation

### 1. The Serialization Process Step by Step

#### Step 1: Stream Initialization
When a serialization stream is created, it writes a header:
- Magic number: identifies this as a serialization stream
- Version number: identifies the protocol version
- These are validated during deserialization

#### Step 2: Object Encountered
When writeObject() is called, the engine determines:
- Is the object null? Write a null marker.
- Has this object been seen? Write existing handle reference.
- Is this a new object? Assign a new handle and proceed.

#### Step 3: Class Descriptor Writing
For new objects, the class descriptor is written:
- Class name as a UTF-encoded string
- serialVersionUID as an 8-byte long value
- Class flags (Serializable, Externalizable, enum)
- Field descriptors: type code and field name for each field

#### Step 4: Field Data Writing
After the descriptor, field values are written sequentially:
- Primitive fields: written directly in binary format
- Object fields: trigger recursive writeObject call
- String fields: written with optimized UTF encoding
- Array fields: written with length prefix and elements
- Collection fields: written as objects with their internal structure

#### Step 5: Graph Completion
The process continues depth-first until all reachable objects are processed.

### 2. The Deserialization Process Step by Step

#### Step 1: Stream Validation
The input stream validates: magic number, version, and initializes the handle table.

#### Step 2: Class Descriptor Reading
For each class encountered: read name and UID, validate against available classes.
UID mismatch throws InvalidClassException. Missing class throws ClassNotFoundException.

#### Step 3: Object Allocation
Objects are allocated without calling constructors, using Unsafe.allocateInstance.
The object starts in default state (null/zero fields).

#### Step 4: Field Population
Fields are populated from the stream by matching field names to class fields.

#### Step 5: Object Completion
After all fields are populated, readObject() and readResolve() are called.

### 3. Reference Tracking
Handles are sequential integers starting from 0x007E0001. Each unique object gets one.
Repeated objects write only the handle. Deserialization resolves handles to objects.

### 4. Class Evolution
serialVersionUID enables controlled class evolution. Compatible changes add fields.
Incompatible changes (removing fields, changing types) require UID change.
