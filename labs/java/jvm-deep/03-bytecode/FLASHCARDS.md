# FLASHCARDS — Bytecode Serialization

| # | Front | Back |
|---|-------|------|
| 1 | Node binary format? | [4B value][4B childCount][children...] |
| 2 | Traversal order? | Pre-order (node → children) |
| 3 | Endianness? | Big-endian (DataOutputStream default) |
| 3 | Int size? | 4 bytes, signed, big-endian |
| 5 | Stream classes? | DataOutputStream / DataInputStream |
| 5 | Traversal order? | Pre-order (node → children) |
| 5 | Recursive vs iterative? | Recursive = simple; iterative for deep trees |
| 6 | Empty tree serialization? | Zero-length byte array |
| 6 | Space per node? | 8 bytes (4B value + 4B child count) + children |
| 6 | Time complexity? | O(N) time, O(N) space |
| 6 | JSON vs binary size? | Binary 2-6x smaller |
| 6 | Large ints? | Use writeLong/readLong or LEB128 |
| 6 | Stream end handling? | EOFException thrown |
| 6 | String support? | Length prefix + UTF-8 bytes |
| 6 | Corrupted stream? | EOFException or garbage values |
| 6 | Deep tree fix? | Iterative with explicit stack or -Xss |
| 6 | Corrupted stream? | EOFException or garbage values |
| 7 | Endianness? | Big-endian (network byte order) |