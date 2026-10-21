# XML Serialization -- Debugging

## Debugging Strategies

### 1. Common Serialization Errors

#### InvalidClassException
Causes: serialVersionUID mismatch between serialized data and class definition.
**Solution:** Ensure serialVersionUID is explicitly declared. Use serialver tool to generate UID.

#### NotSerializableException
Causes: An object in the graph does not implement Serializable.
**Solution:** Make the class Serializable or mark it as transient.

#### StreamCorruptedException
Causes: Stream data is corrupted or not a valid serialization stream.
**Solution:** Verify stream integrity. Check for truncation or encoding issues.

#### OptionalDataException
Causes: Mismatch between write and read calls (wrong number of primitives).
**Solution:** Ensure writeObject/readObject are perfectly symmetrical.

### 2. Debugging Tools

#### Serialization Stream Inspection
`ash
# Use serialver to check serialVersionUID
serialver com.javalab.MyClass

# Analyze serialized file with od/hexdump
od -A x -t x1z -v data.ser | head -20
`

#### JVM Flags for Serialization Debugging
`ash
-XX:+HeapDumpOnOutOfMemoryError
-XX:HeapDumpPath=/tmp/dump.hprof
-Dsun.io.serialization.extendedDebugInfo=true
`

#### IDE Debugging
- Set breakpoints in writeObject/readObject
- Use IntelliJ's built-in serialization inspector
- Examine object graphs during serialization

### 3. Heap Dump Analysis
When deserialization causes OOM:
1. Analyze heap dump with Eclipse MAT
2. Look for serialization-related objects
3. Check for object graphs that are too deep or wide
4. Identify leaked objects from deserialization

### 4. Thread Dump Analysis
When serialization hangs:
1. Capture thread dump with jstack
2. Look for threads blocked in I/O operations
3. Check for deadlocks in custom writeObject/readObject
4. Verify stream closure in finally blocks

### 5. Logging Strategies
`java
// Log serialization events
private void writeObject(ObjectOutputStream oos) throws IOException {
    logger.debug(""Serializing: {}"", this);
    oos.defaultWriteObject();
    logger.debug(""Serialization complete for: {}"", this);
}
`

### 6. Proactive Debugging Checklist
- [ ] All serializable classes have serialVersionUID
- [ ] writeObject/readObject are symmetrical
- [ ] Transient fields are properly initialized after deserialization
- [ ] Custom serialization handles null values
- [ ] Streams are closed in finally blocks
- [ ] Security filters are configured
- [ ] Version compatibility is tested
