package com.learning.io;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.MappedByteBuffer;
import java.nio.channels.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.nio.file.attribute.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;
import java.util.zip.*;

/**
 * Elite File I/O & NIO Training - FAANG Interview Preparation
 *
 * 12 Advanced File I/O Problems organized by difficulty:
 * - Foundation Level (Problems 1-4): Basic I/O operations
 * - Intermediate Level (Problems 5-8): NIO.2 and advanced operations
 * - Advanced Level (Problems 9-12): Performance and scalability
 *
 * Each problem includes:
 * - Company attribution (Google, Amazon, Meta, Microsoft, Netflix, LinkedIn)
 * - Time/Space complexity analysis
 * - Interview tips and best practices
 * - Multiple approaches where applicable
 *
 * @author Elite Java Learning Platform
 * @version 1.0
 */
public class EliteFileIOTraining {

    /**
     * PROBLEM 1: Read Large File Line by Line
     * Companies: Google, Amazon
     * Difficulty: Easy-Medium
     *
     * Read a large file efficiently without loading entire file into memory.
     * Process each line and return line count and total size.
     *
     * Time Complexity: O(n) - where n is number of lines
     * Space Complexity: O(1) - constant memory usage
     *
     * Interview Tip: Use BufferedReader for text files, explain why it's better
     * than reading entire file at once. Discuss memory efficiency.
     */
    public static class FileStats {
        private final long lineCount;
        private final long totalChars;
        private final long fileSize;

        public FileStats(long lineCount, long totalChars, long fileSize) {
            this.lineCount = lineCount;
            this.totalChars = totalChars;
            this.fileSize = fileSize;
        }

        public long getLineCount() { return lineCount; }
        public long getTotalChars() { return totalChars; }
        public long getFileSize() { return fileSize; }
    }

    public static FileStats readFileLazily(Path filePath) throws IOException {
        long lineCount = 0;
        long totalChars = 0;

        try (BufferedReader reader = Files.newBufferedReader(filePath, StandardCharsets.UTF_8)) {
            String line;
            while ((line = reader.readLine()) != null) {
                lineCount++;
                totalChars += line.length();
            }
        }

        long fileSize = Files.size(filePath);
        return new FileStats(lineCount, totalChars, fileSize);
    }

    /**
     * PROBLEM 2: Copy File with Progress Tracking
     * Companies: Amazon, Meta
     * Difficulty: Medium
     *
     * Copy file from source to destination with progress callback.
     * Handle large files efficiently using buffering.
     *
     * Time Complexity: O(n) - where n is file size
     * Space Complexity: O(1) - fixed buffer size
     *
     * Interview Tip: Discuss buffer size trade-offs. Larger buffer = fewer I/O
     * operations but more memory. Common sizes: 4KB, 8KB, 16KB.
     */
    @FunctionalInterface
    public interface ProgressCallback {
        void onProgress(long bytesRead, long totalBytes);
    }

    public static void copyFileWithProgress(Path source, Path destination,
                                           ProgressCallback callback) throws IOException {
        long totalBytes = Files.size(source);
        long bytesRead = 0;
        byte[] buffer = new byte[8192]; // 8KB buffer

        try (InputStream in = Files.newInputStream(source);
             OutputStream out = Files.newOutputStream(destination)) {

            int read;
            while ((read = in.read(buffer)) != -1) {
                out.write(buffer, 0, read);
                bytesRead += read;
                if (callback != null) {
                    callback.onProgress(bytesRead, totalBytes);
                }
            }
        }
    }

    /**
     * PROBLEM 3: Find Files by Pattern Using NIO
     * Companies: Google, Microsoft
     * Difficulty: Medium
     *
     * Recursively find all files matching a pattern in a directory tree.
     * Use NIO.2 for efficient directory traversal.
     *
     * Time Complexity: O(n) - where n is total number of files/directories
     * Space Complexity: O(d) - where d is maximum directory depth
     *
     * Interview Tip: Explain Files.walk() vs Files.walkFileTree().
     * walk() is simpler, walkFileTree() offers more control.
     */
    public static List<Path> findFilesByPattern(Path rootPath, String pattern)
            throws IOException {
        List<Path> results = new ArrayList<>();

        try (Stream<Path> paths = Files.walk(rootPath)) {
            paths.filter(Files::isRegularFile)
                 .filter(path -> path.getFileName().toString().matches(pattern))
                 .forEach(results::add);
        }

        return results;
    }

    /**
     * Alternative using PathMatcher for glob patterns
     */
    public static List<Path> findFilesByGlob(Path rootPath, String globPattern)
            throws IOException {
        List<Path> results = new ArrayList<>();
        PathMatcher matcher = FileSystems.getDefault()
            .getPathMatcher("glob:" + globPattern);

        try (Stream<Path> paths = Files.walk(rootPath)) {
            paths.filter(Files::isRegularFile)
                 .filter(path -> matcher.matches(path.getFileName()))
                 .forEach(results::add);
        }

        return results;
    }

    /**
     * PROBLEM 4: Watch Directory for Changes
     * Companies: Netflix, Amazon
     * Difficulty: Medium-Hard
     *
     * Implement a directory watcher that monitors file system events
     * (create, modify, delete) using WatchService API.
     *
     * Time Complexity: O(1) - event-driven
     * Space Complexity: O(n) - where n is number of events in queue
     *
     * Interview Tip: Discuss use cases (hot reload, file sync).
     * Explain WatchService is more efficient than polling.
     */
    public static class DirectoryWatcher {
        private final WatchService watchService;
        private final Path directory;
        private volatile boolean running;

        public DirectoryWatcher(Path directory) throws IOException {
            this.directory = directory;
            this.watchService = FileSystems.getDefault().newWatchService();

            directory.register(watchService,
                StandardWatchEventKinds.ENTRY_CREATE,
                StandardWatchEventKinds.ENTRY_MODIFY,
                StandardWatchEventKinds.ENTRY_DELETE);
        }

        public List<FileEvent> pollEvents(long timeoutMs) throws InterruptedException {
            List<FileEvent> events = new ArrayList<>();
            WatchKey key = watchService.poll(timeoutMs, TimeUnit.MILLISECONDS);

            if (key != null) {
                for (WatchEvent<?> event : key.pollEvents()) {
                    WatchEvent.Kind<?> kind = event.kind();

                    if (kind == StandardWatchEventKinds.OVERFLOW) {
                        continue;
                    }

                    @SuppressWarnings("unchecked")
                    WatchEvent<Path> pathEvent = (WatchEvent<Path>) event;
                    Path filename = pathEvent.context();

                    events.add(new FileEvent(kind.name(), filename.toString()));
                }

                key.reset();
            }

            return events;
        }

        public void close() throws IOException {
            watchService.close();
        }
    }

    public static class FileEvent {
        private final String eventType;
        private final String fileName;

        public FileEvent(String eventType, String fileName) {
            this.eventType = eventType;
            this.fileName = fileName;
        }

        public String getEventType() { return eventType; }
        public String getFileName() { return fileName; }
    }

    /**
     * PROBLEM 5: Efficient File Comparison
     * Companies: Google, LinkedIn
     * Difficulty: Medium
     *
     * Compare two files efficiently. For small files use byte-by-byte comparison.
     * For large files use checksums or memory-mapped files.
     *
     * Time Complexity: O(n) - where n is file size
     * Space Complexity: O(1) - constant buffer
     *
     * Interview Tip: Discuss trade-offs between accuracy and performance.
     * Checksums are fast but have collision risk. Byte comparison is accurate.
     */
    public static boolean compareFiles(Path file1, Path file2) throws IOException {
        // Quick size check
        if (Files.size(file1) != Files.size(file2)) {
            return false;
        }

        // For small files, use byte comparison
        if (Files.size(file1) < 10 * 1024 * 1024) { // < 10MB
            return compareFilesByteByByte(file1, file2);
        } else {
            // For large files, use memory-mapped I/O
            return compareFilesMemoryMapped(file1, file2);
        }
    }

    private static boolean compareFilesByteByByte(Path file1, Path file2)
            throws IOException {
        try (InputStream in1 = Files.newInputStream(file1);
             InputStream in2 = Files.newInputStream(file2)) {

            byte[] buffer1 = new byte[8192];
            byte[] buffer2 = new byte[8192];

            int read1, read2;
            while ((read1 = in1.read(buffer1)) != -1) {
                read2 = in2.read(buffer2);

                if (read1 != read2) {
                    return false;
                }

                if (!Arrays.equals(buffer1, 0, read1, buffer2, 0, read2)) {
                    return false;
                }
            }

            return in2.read() == -1; // Ensure both files are fully read
        }
    }

    private static boolean compareFilesMemoryMapped(Path file1, Path file2)
            throws IOException {
        try (FileChannel channel1 = FileChannel.open(file1, StandardOpenOption.READ);
             FileChannel channel2 = FileChannel.open(file2, StandardOpenOption.READ)) {

            long size = channel1.size();
            long chunkSize = 1024 * 1024; // 1MB chunks

            for (long position = 0; position < size; position += chunkSize) {
                long remaining = Math.min(chunkSize, size - position);

                ByteBuffer buffer1 = channel1.map(
                    FileChannel.MapMode.READ_ONLY, position, remaining);
                ByteBuffer buffer2 = channel2.map(
                    FileChannel.MapMode.READ_ONLY, position, remaining);

                try {
                    if (!buffer1.equals(buffer2)) {
                        return false;
                    }
                } finally {
                    unmap(buffer1);
                    unmap(buffer2);
                }
            }

            return true;
        }
    }

    /**
     * Force-unmaps a mapped buffer so Windows releases the file lock.
     * Without this, {@code @TempDir} cleanup fails on Windows because the
     * mapping keeps the file open even after the channel is closed.
     * Uses {@code sun.misc.Unsafe#invokeCleaner} (public API since Java 9,
     * no {@code --add-opens} required).
     */
    private static void unmap(ByteBuffer buffer) {
        if (buffer instanceof MappedByteBuffer mapped) {
            try {
                Class<?> unsafeClass = Class.forName("sun.misc.Unsafe");
                java.lang.reflect.Field theUnsafe = unsafeClass.getDeclaredField("theUnsafe");
                theUnsafe.setAccessible(true);
                Object unsafe = theUnsafe.get(null);
                unsafeClass.getMethod("invokeCleaner", ByteBuffer.class).invoke(unsafe, mapped);
            } catch (Exception ignored) {
                // Best-effort: GC will eventually release the mapping.
            }
        }
    }

    /**
     * PROBLEM 6: Serialize and Deserialize Objects
     * Companies: Amazon, Meta
     * Difficulty: Medium
     *
     * Implement safe serialization and deserialization with versioning.
     * Handle SerialVersionUID and custom serialization.
     *
     * Time Complexity: O(n) - where n is object size
     * Space Complexity: O(n) - serialized form
     *
     * Interview Tip: Discuss security risks of deserialization.
     * Explain transient fields and custom readObject/writeObject.
     */
    public static class SerializableUser implements Serializable {
        private static final long serialVersionUID = 1L;

        private String username;
        private String email;
        private transient String password; // Not serialized for security
        private int loginCount;

        public SerializableUser(String username, String email, String password) {
            this.username = username;
            this.email = email;
            this.password = password;
            this.loginCount = 0;
        }

        // Custom serialization for additional security
        private void writeObject(ObjectOutputStream out) throws IOException {
            out.defaultWriteObject();
            // Could encrypt sensitive data here
        }

        private void readObject(ObjectInputStream in)
                throws IOException, ClassNotFoundException {
            in.defaultReadObject();
            // Could decrypt sensitive data here
            this.password = null; // Ensure password is never deserialized
        }

        public String getUsername() { return username; }
        public String getEmail() { return email; }
        public String getPassword() { return password; }
        public int getLoginCount() { return loginCount; }
        public void incrementLoginCount() { loginCount++; }
    }

    public static void serializeObject(Object obj, Path filePath) throws IOException {
        try (ObjectOutputStream out = new ObjectOutputStream(
                Files.newOutputStream(filePath))) {
            out.writeObject(obj);
        }
    }

    public static <T> T deserializeObject(Path filePath, Class<T> type)
            throws IOException, ClassNotFoundException {
        try (ObjectInputStream in = new ObjectInputStream(
                Files.newInputStream(filePath))) {
            Object obj = in.readObject();
            return type.cast(obj);
        }
    }

    /**
     * PROBLEM 7: Read and Write CSV Files
     * Companies: Google, Amazon
     * Difficulty: Medium
     *
     * Parse CSV files handling edge cases (quotes, commas in fields, newlines).
     * Write CSV with proper escaping.
     *
     * Time Complexity: O(n*m) - n rows, m columns
     * Space Complexity: O(m) - one row at a time
     *
     * Interview Tip: Discuss CSV edge cases. Fields with commas must be quoted.
     * Quotes inside fields must be escaped as double quotes.
     */
    public static class CSVReader {
        private final BufferedReader reader;

        public CSVReader(Path filePath) throws IOException {
            this.reader = Files.newBufferedReader(filePath, StandardCharsets.UTF_8);
        }

        public List<String> readRow() throws IOException {
            String line = reader.readLine();
            if (line == null) {
                return null;
            }

            return parseCSVLine(line);
        }

        private List<String> parseCSVLine(String line) {
            List<String> fields = new ArrayList<>();
            StringBuilder current = new StringBuilder();
            boolean inQuotes = false;

            for (int i = 0; i < line.length(); i++) {
                char c = line.charAt(i);

                if (c == '"') {
                    // Check for escaped quote
                    if (inQuotes && i + 1 < line.length() && line.charAt(i + 1) == '"') {
                        current.append('"');
                        i++; // Skip next quote
                    } else {
                        inQuotes = !inQuotes;
                    }
                } else if (c == ',' && !inQuotes) {
                    fields.add(current.toString());
                    current.setLength(0);
                } else {
                    current.append(c);
                }
            }

            fields.add(current.toString());
            return fields;
        }

        public List<List<String>> readAll() throws IOException {
            List<List<String>> allRows = new ArrayList<>();
            List<String> row;
            while ((row = readRow()) != null) {
                allRows.add(row);
            }
            return allRows;
        }

        public void close() throws IOException {
            reader.close();
        }
    }

    public static class CSVWriter {
        private final BufferedWriter writer;

        public CSVWriter(Path filePath) throws IOException {
            this.writer = Files.newBufferedWriter(filePath, StandardCharsets.UTF_8);
        }

        public void writeRow(List<String> fields) throws IOException {
            for (int i = 0; i < fields.size(); i++) {
                if (i > 0) {
                    writer.write(',');
                }
                writer.write(escapeCSVField(fields.get(i)));
            }
            writer.newLine();
        }

        private String escapeCSVField(String field) {
            if (field.contains(",") || field.contains("\"") || field.contains("\n")) {
                // Escape quotes and wrap in quotes
                return "\"" + field.replace("\"", "\"\"") + "\"";
            }
            return field;
        }

        public void close() throws IOException {
            writer.close();
        }
    }

    /**
     * PROBLEM 8: File Compression and Decompression
     * Companies: Netflix, Google
     * Difficulty: Medium-Hard
     *
     * Compress and decompress files using GZIP or ZIP format.
     * Handle large files with streaming.
     *
     * Time Complexity: O(n) - where n is file size
     * Space Complexity: O(1) - fixed buffer
     *
     * Interview Tip: Discuss compression algorithms (GZIP, ZIP, BZIP2).
     * Explain trade-offs between compression ratio and speed.
     */
    public static void compressFile(Path source, Path destination) throws IOException {
        try (InputStream in = Files.newInputStream(source);
             OutputStream out = Files.newOutputStream(destination);
             GZIPOutputStream gzipOut = new GZIPOutputStream(out)) {

            byte[] buffer = new byte[8192];
            int read;
            while ((read = in.read(buffer)) != -1) {
                gzipOut.write(buffer, 0, read);
            }
        }
    }

    public static void decompressFile(Path source, Path destination) throws IOException {
        try (InputStream in = Files.newInputStream(source);
             GZIPInputStream gzipIn = new GZIPInputStream(in);
             OutputStream out = Files.newOutputStream(destination)) {

            byte[] buffer = new byte[8192];
            int read;
            while ((read = gzipIn.read(buffer)) != -1) {
                out.write(buffer, 0, read);
            }
        }
    }

    /**
     * Create ZIP archive with multiple files
     */
    public static void createZipArchive(Path outputZip, Map<String, Path> files)
            throws IOException {
        try (ZipOutputStream zos = new ZipOutputStream(
                Files.newOutputStream(outputZip))) {

            for (Map.Entry<String, Path> entry : files.entrySet()) {
                ZipEntry zipEntry = new ZipEntry(entry.getKey());
                zos.putNextEntry(zipEntry);

                Files.copy(entry.getValue(), zos);
                zos.closeEntry();
            }
        }
    }

    /**
     * PROBLEM 9: Memory-Mapped File I/O
     * Companies: Google, LinkedIn
     * Difficulty: Hard
     *
     * Use memory-mapped files for high-performance I/O operations.
     * Demonstrate when memory mapping is beneficial.
     *
     * Time Complexity: O(1) for access, O(n) for sequential scan
     * Space Complexity: O(1) - OS manages memory mapping
     *
     * Interview Tip: Memory-mapped I/O is fast for random access.
     * Best for large files accessed frequently. Not suitable for all use cases.
     */
    public static class MemoryMappedFile {
        private final FileChannel channel;
        private final MappedByteBuffer buffer;
        private final long size;

        public MemoryMappedFile(Path filePath, boolean readOnly) throws IOException {
            this.channel = readOnly
                ? FileChannel.open(filePath, StandardOpenOption.READ)
                : FileChannel.open(filePath,
                    StandardOpenOption.READ, StandardOpenOption.WRITE);

            this.size = channel.size();
            this.buffer = channel.map(
                readOnly ? FileChannel.MapMode.READ_ONLY : FileChannel.MapMode.READ_WRITE,
                0, size);
        }

        public byte readByte(long position) {
            return buffer.get((int) position);
        }

        public void writeByte(long position, byte value) {
            buffer.put((int) position, value);
        }

        public byte[] read(long position, int length) {
            byte[] data = new byte[length];
            buffer.position((int) position);
            buffer.get(data);
            return data;
        }

        public void write(long position, byte[] data) {
            buffer.position((int) position);
            buffer.put(data);
        }

        public long size() {
            return size;
        }

        public void force() {
            buffer.force();
        }

        public void close() throws IOException {
            unmap(buffer);
            channel.close();
        }
    }

    /**
     * PROBLEM 10: File Lock for Concurrent Access
     * Companies: Amazon, Microsoft
     * Difficulty: Hard
     *
     * Implement file locking to prevent concurrent modification.
     * Use both shared (read) and exclusive (write) locks.
     *
     * Time Complexity: O(1) - lock acquisition
     * Space Complexity: O(1)
     *
     * Interview Tip: Explain shared vs exclusive locks. Multiple readers can
     * hold shared lock, but exclusive lock blocks all other locks.
     */
    public static class FileLockManager {
        private final FileChannel channel;
        private FileLock lock;

        public FileLockManager(Path filePath) throws IOException {
            this.channel = FileChannel.open(filePath,
                StandardOpenOption.READ, StandardOpenOption.WRITE);
        }

        public boolean acquireSharedLock(long timeoutMs) throws IOException {
            try {
                lock = channel.tryLock(0, Long.MAX_VALUE, true);
                return lock != null;
            } catch (OverlappingFileLockException e) {
                return false;
            }
        }

        public boolean acquireExclusiveLock(long timeoutMs) throws IOException {
            try {
                lock = channel.tryLock(0, Long.MAX_VALUE, false);
                return lock != null;
            } catch (OverlappingFileLockException e) {
                return false;
            }
        }

        public void releaseLock() throws IOException {
            if (lock != null && lock.isValid()) {
                lock.release();
                lock = null;
            }
        }

        public boolean isLocked() {
            return lock != null && lock.isValid();
        }

        public void close() throws IOException {
            releaseLock();
            channel.close();
        }
    }

    /**
     * PROBLEM 11: Asynchronous File I/O
     * Companies: Netflix, Google
     * Difficulty: Hard
     *
     * Implement asynchronous file operations using AsynchronousFileChannel.
     * Demonstrate non-blocking I/O with CompletableFuture.
     *
     * Time Complexity: O(n) - file size
     * Space Complexity: O(1) - fixed buffer
     *
     * Interview Tip: Async I/O is beneficial when I/O operations are the bottleneck.
     * CPU can do other work while waiting for I/O completion.
     */
    public static CompletableFuture<String> readFileAsync(Path filePath) {
        CompletableFuture<String> future = new CompletableFuture<>();

        try {
            AsynchronousFileChannel channel = AsynchronousFileChannel.open(
                filePath, StandardOpenOption.READ);

            long fileSize = channel.size();
            ByteBuffer buffer = ByteBuffer.allocate((int) fileSize);

            channel.read(buffer, 0, buffer, new CompletionHandler<Integer, ByteBuffer>() {
                @Override
                public void completed(Integer result, ByteBuffer attachment) {
                    attachment.flip();
                    String content = StandardCharsets.UTF_8.decode(attachment).toString();
                    future.complete(content);

                    try {
                        channel.close();
                    } catch (IOException e) {
                        future.completeExceptionally(e);
                    }
                }

                @Override
                public void failed(Throwable exc, ByteBuffer attachment) {
                    future.completeExceptionally(exc);
                    try {
                        channel.close();
                    } catch (IOException ignored) {}
                }
            });

        } catch (IOException e) {
            future.completeExceptionally(e);
        }

        return future;
    }

    /**
     * PROBLEM 12: Directory Tree Copy
     * Companies: Google, Amazon
     * Difficulty: Hard
     *
     * Recursively copy entire directory tree including permissions and attributes.
     * Handle symbolic links and preserve file metadata.
     *
     * Time Complexity: O(n) - where n is total files/directories
     * Space Complexity: O(d) - where d is maximum depth
     *
     * Interview Tip: Discuss COPY_ATTRIBUTES option to preserve metadata.
     * Explain handling of symbolic links (NOFOLLOW_LINKS).
     */
    public static void copyDirectory(Path source, Path destination,
                                     boolean preserveAttributes) throws IOException {
        Files.walkFileTree(source, new SimpleFileVisitor<Path>() {
            @Override
            public FileVisitResult preVisitDirectory(Path dir, BasicFileAttributes attrs)
                    throws IOException {
                Path targetDir = destination.resolve(source.relativize(dir));
                Files.createDirectories(targetDir);

                if (preserveAttributes) {
                    Files.setAttribute(targetDir, "creationTime",
                        attrs.creationTime());
                }

                return FileVisitResult.CONTINUE;
            }

            @Override
            public FileVisitResult visitFile(Path file, BasicFileAttributes attrs)
                    throws IOException {
                Path targetFile = destination.resolve(source.relativize(file));

                if (preserveAttributes) {
                    Files.copy(file, targetFile,
                        StandardCopyOption.COPY_ATTRIBUTES,
                        StandardCopyOption.REPLACE_EXISTING);
                } else {
                    Files.copy(file, targetFile,
                        StandardCopyOption.REPLACE_EXISTING);
                }

                return FileVisitResult.CONTINUE;
            }
        });
    }

    /**
     * Main method to demonstrate all File I/O patterns
     */
    public static void main(String[] args) {
        System.out.println("╔════════════════════════════════════════════════════════════════╗");
        System.out.println("║      ELITE FILE I/O & NIO TRAINING - 12 FAANG PROBLEMS       ║");
        System.out.println("╚════════════════════════════════════════════════════════════════╝");

        demonstrateFoundationProblems();
        demonstrateIntermediateProblems();
        demonstrateAdvancedProblems();

        System.out.println("\n" + "═".repeat(70));
        System.out.println("🎓 ELITE FILE I/O TRAINING COMPLETE!");
        System.out.println("═".repeat(70));
        System.out.println("\nYou have mastered:");
        System.out.println("  ✓ Efficient file reading (lazy, buffered)");
        System.out.println("  ✓ File copying with progress tracking");
        System.out.println("  ✓ Directory traversal and pattern matching");
        System.out.println("  ✓ File system monitoring (WatchService)");
        System.out.println("  ✓ File comparison algorithms");
        System.out.println("  ✓ Object serialization and deserialization");
        System.out.println("  ✓ CSV parsing and generation");
        System.out.println("  ✓ File compression and decompression");
        System.out.println("  ✓ Memory-mapped file I/O");
        System.out.println("  ✓ File locking for concurrency");
        System.out.println("  ✓ Asynchronous file operations");
        System.out.println("  ✓ Directory tree operations");
        System.out.println("\n✨ Ready for FAANG File I/O interviews!");
    }

    private static void demonstrateFoundationProblems() {
        System.out.println("\n" + "═".repeat(70));
        System.out.println("FOUNDATION LEVEL (Problems 1-4)");
        System.out.println("═".repeat(70));

        System.out.println("\n1. Read Large File Line by Line (Google, Amazon)");
        System.out.println("   Pattern: Lazy loading with BufferedReader");

        System.out.println("\n2. Copy File with Progress (Amazon, Meta)");
        System.out.println("   Pattern: Buffered I/O with callbacks");

        System.out.println("\n3. Find Files by Pattern (Google, Microsoft)");
        System.out.println("   Pattern: NIO.2 directory traversal");

        System.out.println("\n4. Watch Directory Changes (Netflix, Amazon)");
        System.out.println("   Pattern: WatchService API");
    }

    private static void demonstrateIntermediateProblems() {
        System.out.println("\n" + "═".repeat(70));
        System.out.println("INTERMEDIATE LEVEL (Problems 5-8)");
        System.out.println("═".repeat(70));

        System.out.println("\n5. Efficient File Comparison (Google, LinkedIn)");
        System.out.println("   Pattern: Byte-by-byte or memory-mapped");

        System.out.println("\n6. Object Serialization (Amazon, Meta)");
        System.out.println("   Pattern: Serializable with custom methods");

        System.out.println("\n7. CSV Read/Write (Google, Amazon)");
        System.out.println("   Pattern: Proper escaping and parsing");

        System.out.println("\n8. File Compression (Netflix, Google)");
        System.out.println("   Pattern: GZIP and ZIP streaming");
    }

    private static void demonstrateAdvancedProblems() {
        System.out.println("\n" + "═".repeat(70));
        System.out.println("ADVANCED LEVEL (Problems 9-12)");
        System.out.println("═".repeat(70));

        System.out.println("\n9. Memory-Mapped File I/O (Google, LinkedIn)");
        System.out.println("   Pattern: High-performance random access");

        System.out.println("\n10. File Locking (Amazon, Microsoft)");
        System.out.println("   Pattern: Shared and exclusive locks");

        System.out.println("\n11. Asynchronous File I/O (Netflix, Google)");
        System.out.println("   Pattern: Non-blocking operations");

        System.out.println("\n12. Directory Tree Copy (Google, Amazon)");
        System.out.println("   Pattern: Recursive traversal with attributes");
    }
}
