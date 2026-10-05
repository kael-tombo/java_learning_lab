# Flashcards — Java IO / NIO Deep

| Q | A |
|---|---|
| Buffer position? | Next read/write index |
| Buffer limit? | First index not to read/write |
| Buffer capacity? | Max size fixed at alloc |
| flip() formula? | limit=pos; pos=0 |
| clear() formula? | pos=0; limit=capacity |
| compact()? | Copy unread to start, pos after them |
| rewind()? | pos=0, limit unchanged |
| mark()/reset()? | Bookmark position |
| Heap buffer? | byte[] backed, GC heap |
| Direct buffer? | Off-heap, no GC move |
| Allocate direct? | ByteBuffer.allocateDirect(n) |
| Selector? | One thread, many channels |
| SelectableChannel? | Must be non-blocking |
| OP_ACCEPT? | Server ready accept |
| OP_CONNECT? | Client connected |
| OP_READ? | Data available |
| OP_WRITE? | Can write w/o block |
| wakeup()? | Unblock select() |
| FileChannel.open opts? | READ/WRITE/CREATE/TRUNCATE |
| transferTo args? | position, count, target |
| transferFrom args? | src, position, count |
| map() modes? | READ_ONLY/READ_WRITE/PRIVATE |
| MappedByteBuffer force()? | Flush to disk |
| Async read handler? | CompletionHandler.completed/failed |
| AsyncChannelGroup? | Pool for async ops |
| WatchService events? | CREATE/MODIFY/DELETE/OVERFLOW |
| WatchKey reset()? | Re-arm for next events |
| Path vs File? | Path is NIO, File legacy |
| Files.copy opts? | REPLACE_EXISTING/COPY_ATTRS |
| Files.walk depth? | walk(p, maxDepth) |
| DirectoryStream? | Lazy dir listing |
| Charset decode error? | CodingErrorAction REPORT/REPLACE |
| StandardOpenOption APPEND? | Writes at end |
| Pipe? | Sink/source channel pair |
| DatagramChannel? | UDP non-blocking |
| SocketChannel blocking? | configureBlocking(false) |
| ServerSocketChannel bind? | bind(new InetSocketAddress(port)) |
| Gathering write? | write(ByteBuffer[]) one syscall |
| Scattering read? | read(ByteBuffer[]) fill each |
| FileLock shared? | Shared read vs exclusive |
| tryLock vs lock? | Non-blocking vs blocking |
| RandomAccessFile mode? | "r","rw","rws","rwd" |
| BufferedReader default? | 8KB buffer |
| PrintWriter autoflush? | Flush on println if set |
| Object stream header? | Written once per stream |
| Serializable UID? | versionId for compat |
| transient? | Skip field in ser |
| Files.isSameFile? | Same inode/file |
| Symbolic link read? | Files.readSymbolicLink |
| LinkOption NOFOLLOW? | Operate on link itself |
| FileStore type? | Files.getFileStore(p) |
| MaxDirectMemorySize flag? | -XX:MaxDirectMemorySize= |
| Cached buffer flag? | -Djdk.nio.maxCachedBufferSize= |
| Temp buffer size? | -Djdk.nio.maxCachedBufferSize |
| lsof leak check? | lsof -p PID |
| strace IO? | strace -e trace=read,write |
| Page cache? | OS caches file pages |
| Zero-copy syscall? | sendfile on Linux |
| Blocking IO thread cost? | ~1MB stack each |
| Backpressure? | Bound queues, drop/shed |
| ByteOrder native? | ByteOrder.nativeOrder() |
| View buffer asIntBuffer? | asIntBuffer()/asCharBuffer() |
| Slice()? | Shares content, own pos |
| Duplicate()? | Shares content+pos copy |
| ReadOnly buffer? | asReadOnlyBuffer() |
| Compact after half-read? | Yes to keep remainder |
| Selector keys()? | All registered keys |
| selectedKeys()? | Ready subset |
| Cancel key? | key.cancel() |
| Attach object? | key.attach(obj)/attachment() |
| Shutdown selector? | Close channels then selector |
| try-with-resources? | Auto-close channels |
| Files.lines charset? | Files.lines(p, UTF_8) |
| Large dir walk OOM? | Use Files.walk lazily + filter |
| Best copy large file? | transferTo zero-copy |
| Best many small conns? | Selector non-blocking |
| Best tail latency? | Async + pooled buffers |
