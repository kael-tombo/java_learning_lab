# THEORY — I/O Streams (lab01)

## 1. The core idea

Java's classic I/O (`java.io`) models data as an ordered **stream of bytes or
characters**. You never "jump around" — you open a stream, read/write
sequentially, and close it. The hierarchy splits on one question: **bytes or
characters?**

- **Byte streams** (`InputStream` / `OutputStream`): binary data — files,
  sockets, images. No encoding interpretation.
- **Character streams** (`Reader` / `Writer`): text — bytes decoded via a
  `Charset` (always specify `StandardCharsets.UTF_8`; the platform default
  is a portability bug waiting to happen).

## 2. The decorator pattern is the whole design

`MainImplementation.bufferedCopy` shows it:

```java
new BufferedInputStream(new FileInputStream(source))
```

Each wrapper adds one capability: `FileInputStream` opens the OS handle,
`BufferedInputStream` adds an 8 KB memory buffer. You compose behavior by
nesting constructors. The GUIDE's sections 1–5 are all instances of this:
`DataInputStream` adds primitive encoding, `PushbackInputStream` adds a
peek buffer, `SequenceInputStream` concatenates sources.

## 3. Why buffering matters (the one number to remember)

A raw `FileInputStream.read()` costs **one syscall per byte**. For a 1 MB
file that is ~1M syscalls. Wrapping in `BufferedInputStream` (or reading
into `byte[8192]`, as `bufferedCopy` does) amortizes this to ~128 syscalls.
Same bytes, ~1000× fewer kernel crossings. This is the single most
important I/O performance fact in the lab.

## 4. Ordering contracts

`writePrimitives` / `readPrimitives` must use the **same order and types**:
`writeInt → writeDouble → writeUTF` pairs with
`readInt → readDouble → readUTF`. There is no schema, no field names —
the format is purely positional. Get the order wrong and you silently read
garbage (or throw `EOFException`).

## 5. Resource discipline

Every stream here is opened in **try-with-resources** and implements
`AutoCloseable`. Close order is reverse of opening. Leaking a
`FileInputStream` leaks an OS file descriptor — on Windows it also locks
the file against deletion (same family of bug as the `MappedByteBuffer`
issue in `07-file-io`, see `docs/guides/MEMORY_MAPPED_FILES_DEEP_DIVE.md`).
