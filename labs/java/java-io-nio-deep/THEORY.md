# THEORY — Java I/O & NIO Deep Dive

## Overview

Java I/O evolved from blocking streams (java.io) to non-blocking channels (java.nio). NIO.2 (Java 7+) added filesystem APIs.

## Classic I/O (java.io)

### Stream Hierarchy

```
InputStream (abstract)
  ├── FileInputStream
  ├── ByteArrayInputStream
  ├── BufferedInputStream
  ├── DataInputStream
  └── ObjectInputStream

OutputStream (abstract)
  ├── FileOutputStream
  ├── ByteArrayOutputStream
  ├── BufferedOutputStream
  ├── DataOutputStream
  └── ObjectOutputStream

Reader/Writer (character streams)
  ├── FileReader/FileWriter
  ├── BufferedReader/BufferedWriter
  ├── InputStreamReader/OutputStreamWriter
  └── PrintWriter
```

### Try-with-Resources

```java
try (BufferedReader br = new BufferedReader(new FileReader("file.txt"))) {
    String line;
    while ((line = br.readLine()) != null) {
        process(line);
    }
}
```

## NIO Channels & Buffers

### Buffer Basics

```java
ByteBuffer buffer = ByteBuffer.allocate(1024);
buffer.put(data);           // write
buffer.flip();              // prepare for read
while (buffer.hasRemaining()) process(buffer.get());
buffer.clear();             // prepare for write
buffer.compact();           // keep unread data
```

### Channel Types

| Channel | Use Case |
|---------|----------|
| `FileChannel` | File I/O with position, mapping |
| `SocketChannel` | TCP client |
| `ServerSocketChannel` | TCP server |
| `DatagramChannel` | UDP |
| `Pipe.SinkChannel/SourceChannel` | Thread communication |

### FileChannel Operations

```java
try (FileChannel ch = FileChannel.open(path, READ, WRITE)) {
    // Positioned read/write
    ch.read(buffer, position);
    ch.write(buffer, position);
    
    // Memory-mapped file
    MappedByteBuffer map = ch.map(READ_ONLY, 0, ch.size());
    
    // Transfer (zero-copy)
    ch.transferTo(0, ch.size(), targetChannel);
    
    // Locking
    FileLock lock = ch.lock(position, size, shared);
}
```

## NIO.2 Filesystem API (java.nio.file)

### Path Operations

```java
Path path = Paths.get("/home/user/file.txt");
Path relativized = path.relativize(Paths.get("/home/user/docs/readme.md"));
Path normalized = path.normalize();
Path resolved = path.resolveSibling("other.txt");
```

### Files Utility

```java
// Read all
String content = Files.readString(path);
List<String> lines = Files.readAllLines(path);
byte[] bytes = Files.readAllBytes(path);

// Write
Files.writeString(path, content, StandardOpenOption.CREATE);
Files.write(path, lines, StandardOpenOption.APPEND);

// Stream processing
try (Stream<String> lines = Files.lines(path)) {
    lines.filter(l -> l.contains("error")).forEach(System.out::println);
}

// Walk tree
Files.walk(root)
    .filter(Files::isRegularFile)
    .filter(p -> p.toString().endsWith(".java"))
    .forEach(System.out::println);

// Watch service
WatchService watcher = FileSystems.getDefault().newWatchService();
path.register(watcher, ENTRY_CREATE, ENTRY_MODIFY, ENTRY_DELETE);
```

### Attributes

```java
BasicFileAttributes attrs = Files.readAttributes(path, BasicFileAttributes.class);
attrs.creationTime();
attrs.lastModifiedTime();
attrs.size();
attrs.isDirectory();

DosFileAttributes dos = Files.readAttributes(path, DosFileAttributes.class);
dos.isHidden(); dos.isReadOnly();

PosixFileAttributes posix = Files.readAttributes(path, PosixFileAttributes.class);
posix.owner(); posix.group(); posix.permissions();
```

## Asynchronous I/O (NIO.2)

```java
AsynchronousFileChannel ch = AsynchronousFileChannel.open(path, READ);
Future<Integer> future = ch.read(buffer, position);
Integer bytesRead = future.get(); // blocking

// Or with callback
ch.read(buffer, position, null, new CompletionHandler<Integer, Void>() {
    public void completed(Integer result, Void attachment) { ... }
    public void failed(Throwable exc, Void attachment) { ... }
});
```

## Selectors (Non-blocking I/O)

```java
Selector selector = Selector.open();
serverChannel.configureBlocking(false);
serverChannel.register(selector, SelectionKey.OP_ACCEPT);

while (selector.select() > 0) {
    for (SelectionKey key : selector.selectedKeys()) {
        if (key.isAcceptable()) accept(key);
        else if (key.isReadable()) read(key);
        else if (key.isWritable()) write(key);
        selector.selectedKeys().remove(key);
    }
}
```

## Performance Comparison

| Operation | java.io | NIO | NIO.2 Async |
|-----------|---------|-----|-------------|
| Small files | Good | Good | Overhead |
| Large files | OK | Better (mmap) | Good |
| Many connections | Thread per conn | Selector | Async |
| Zero-copy | No | transferTo | transferTo |

## Serialization

```java
// Java serialization
try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream("obj.ser"))) {
    oos.writeObject(object);
}

// Externalizable (custom)
public class User implements Externalizable {
    public void writeExternal(ObjectOutput out) throws IOException { ... }
    public void readExternal(ObjectInput in) throws IOException { ... }
}
```

## Best Practices

1. **Always use try-with-resources**
2. **Prefer NIO.2 Files API** for filesystem operations
3. **Use Buffered streams** for classic I/O
4. **Memory-map large files** for random access
5. **Use transferTo** for file-to-socket copies
6. **Configure blocking=false** for scalable servers