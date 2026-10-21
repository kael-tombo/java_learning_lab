# Netty Framework -- Why It Exists
## Historical Context and Motivation

### The Problem
Before standardized networking APIs, each operating system had its own
networking interface (Berkeley Sockets, Winsock, etc.). Cross-platform
network programming required platform-specific code.

### Java's Solution
Java's networking APIs provided cross-platform abstraction. The same Socket
code works on Windows, Linux, and macOS without modification.

### Why NIO Exists
The original blocking I/O model could not scale to thousands of concurrent
connections. NIO's Selector enables a single thread to manage many connections.

### Why Netty Exists
Building robust NIO applications requires significant expertise. Netty provides
a proven, well-tested framework that handles edge cases and performance tuning.

### Why gRPC Exists
Traditional REST APIs lack features for streaming, bidirectional communication,
and efficient binary serialization. gRPC addresses these limitations.
