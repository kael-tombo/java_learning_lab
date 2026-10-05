# TCP/UDP - MINI PROJECT

## Project: Wireline — TCP echo (blocking and NIO) plus a reliable UDP protocol you build

Three servers in one project: a blocking TCP echo, a selector-based NIO echo, and a
UDP protocol that adds reliability, ordering, and congestion control on top of datagrams.
Then a benchmark comparing all three.

### Architecture

```
  CLIENTS                    SERVER
  ───────                    ──────
  TCP blocking  ──────────▶  accept → thread-per-connection, read loop
  TCP NIO       ──────────▶  one Selector thread, OP_READ on many channels
  UDP client    ──────────▶  DatagramSocket, parse header, SEQ/ACK, retransmit timer

  UDP reliability layer (what TCP gives you, built by hand):
    ┌────────────┬───────────┬──────────┬──────────┬─────────┐
    │ SEQ (4B)   │ ACK (4B)  │ FLAGS(1) │ LEN (2B) │ payload │
    └────────────┴───────────┴──────────┴──────────┴─────────┘
    Sender keeps a window; receiver ACKs cumulatively; unacked packets retransmit
    on a timeout with exponential backoff. A checksum detects corruption.
```

### Implementation

Blocking TCP server, and the read-partial problem that every beginner hits:

```java
public class TcpEchoServer implements AutoCloseable {
    private final ServerSocket server;
    private final ExecutorService workers = Executors.newVirtualThreadPerTaskExecutor();  // Java 21

    public TcpEchoServer(int port, int backlog) throws IOException {
        // SO_REUSEADDR avoids TIME_WAIT bind failures on restart in a container.
        server = new ServerSocket();
        server.setReuseAddress(true);
        server.bind(new InetSocketAddress(port), backlog);
    }

    public void start() throws IOException {
        while (!server.isClosed()) {
            Socket socket = server.accept();
            // SO_TIMEOUT: a read that never completes would otherwise hold a virtual
            // thread forever. 30s of silence on an echo connection means something is wrong.
            socket.setSoTimeout(30_000);
            workers.submit(() -> handle(socket));
        }
    }

    private void handle(Socket socket) {
        try (socket) {
            socket.setTcpNoDelay(true);       // disable Nagle: this protocol sends small messages
            var in = new BufferedInputStream(socket.getInputStream());
            var out = new BufferedOutputStream(socket.getOutputStream());
            var buffer = new byte[8192];
            while (true) {
                int read;
                try { read = in.read(buffer); }
                catch (SocketTimeoutException e) { break; }     // idle -> close
                if (read == -1) break;
                // read() may return FEWER bytes than were sent. TCP is a byte stream, not
                // a message protocol. Line framing makes the message boundary explicit.
                String line = new String(buffer, 0, read, US_ASCII);
                out.write(("ECHO:" + line).getBytes(US_ASCII));
                out.write('\n');
                out.flush();
            }
        } catch (IOException e) {
            metrics.counter("tcp.connection.error", "cause", e.getClass().getSimpleName()).increment();
        }
    }
}
```

NIO selector server, handling many connections on one thread:

```java
public class NioEchoServer implements AutoCloseable {
    private final Selector selector;
    private final ServerSocketChannel server;
    private final Queue<ByteBuffer> pendingWrites = new ArrayDeque<>();  // per-attachment queue

    public NioEchoServer(int port) throws IOException {
        selector = Selector.open();
        server = ServerSocketChannel.open();
        server.configureBlocking(false);
        server.socket().setReuseAddress(true);
        server.bind(new InetSocketAddress(port), 128);
        server.register(selector, SelectionKey.OP_ACCEPT);
    }

    public void run() throws IOException {
        while (true) {
            // block() with no timeout parks the thread when there is nothing to do.
            selector.select();
            for (SelectionKey key : selector.selectedKeys()) {
                if (key.isAcceptable()) onAccept();
                else if (key.isReadable()) onRead(key);
            }
            selector.selectedKeys().clear();
        }
    }

    private void onAccept() throws IOException {
        SocketChannel ch = server.accept();
        ch.configureBlocking(false);
        ch.socket().setTcpNoDelay(true);
        ch.register(selector, SelectionKey.OP_READ, new ConnectionState());
    }

    private void onRead(SelectionKey key) throws IOException {
        SocketChannel ch = (SocketChannel) key.channel();
        var buf = (ByteBuffer) key.attachment();
        buf.clear();
        int n = ch.read(buf);            // returns 0 for a spurious wakeup - not an error
        if (n == -1) { key.cancel(); ch.close(); return; }
        if (n > 0) {
            buf.flip();
            byte[] data = new byte[n];
            buf.get(data);
            // Never block on write in the selector thread. Queue it and enable OP_WRITE.
            ((ConnectionState) key.attachment()).out.add(ByteBuffer.wrap(("ECHO:" + new String(data, US_ASCII)).getBytes(US_ASCII)));
            key.interestOps(SelectionKey.OP_READ | SelectionKey.OP_WRITE);
        }
    }
}
```

Reliable UDP, implementing what TCP normally provides:

```java
public class ReliableUdpEndpoint {
    private record Header(int seq, int ack, byte flags, int length) {}
    private static final int WINDOW = 32, MAX_RETRANSMITS = 5, TIMEOUT_MS = 200;

    private final DatagramSocket socket;
    private final Map<Integer, PendingPacket> unacked = new LinkedHashMap<>();
    private int nextSeq = 0, expectedAck = 0;

    public void send(byte[] payload) throws IOException {
        while (unacked.size() >= WINDOW) waitForAck();      // sender-side flow control
        int seq = nextSeq++;
        byte[] packet = encode(new Header(seq, expectedAck, FLAG_DATA, payload.length), payload);
        socket.send(new DatagramPacket(packet, packet.length, remote));
        unacked.put(seq, new PendingPacket(packet, payload.length, System.currentTimeMillis(), 0));
    }

    /** Caller loop: retransmit on timeout with backoff, and process inbound ACKs. */
    public void poll() throws IOException {
        long now = System.currentTimeMillis();
        for (var e : new ArrayList<>(unacked.entrySet())) {
            PendingPacket p = e.getValue();
            long deadline = p.sentAt() + (long) (TIMEOUT_MS * Math.pow(2, p.retries()));
            if (now > deadline) {
                if (p.retries() >= MAX_RETRANSMITS) throw new UnreliableTransferException(p.seq());
                socket.send(new DatagramPacket(p.bytes(), p.bytes().length, remote));
                unacked.put(p.seq(), p.retried(p.retries() + 1));
            }
        }
        byte[] buf = new byte[65535];
        DatagramSocket packet = new DatagramSocket(buf.length);
        socket.setSoTimeout(1);                              // non-blocking-ish receive
        try {
            socket.receive(packet);
            Header h = decodeHeader(Arrays.copyOf(packet.getData(), packet.getLength()));
            if ((h.flags() & FLAG_ACK) != 0) {                // cumulative ACK: everything below is received
                unacked.keySet().removeIf(seq -> seq < h.ack());
                expectedAck = h.ack();
            }
            if ((h.flags() & FLAG_DATA) != 0) {
                deliverOnce(payloadFrom(packet));             // deliver only in-order, buffer gaps
                sendAck(nextExpectedToReceive());
            }
        } catch (SocketTimeoutException ignored) { /* no data this tick */ }
    }
}
```

### Test It

```java
@Test void tcpDeliversBytesInOrderRegardlessOfWriteSize() throws Exception {
    try (var server = new TcpEchoServer(0)) { server.start();
        try (var client = new Socket("localhost", server.port())) {
            client.getOutputStream().write("hello world".getBytes(US_ASCII));
            assertThat(readLine(client)).isEqualTo("ECHO:hello world");
        }
    }
}

@Test void nioHandlesManyConcurrentConnectionsOnOneThread() throws Exception {
    try (var server = new NioEchoServer(0)) { server.start();
        IntStream.range(0, 200).parallel().forEach(i -> echoOnce(server.port(), "msg" + i));
        assertThat(server.singleThread()).isTrue();
    }
}

@Test void reliableUdpRecoversFromPacketLoss() throws Exception {
    var lossy = new LossyChannel(0.3);                     // drop 30% of datagrams
    try (var client = reliableEndpoint(); var server = reliableEndpoint()) {
        client.channel(lossy);
        for (int i = 0; i < 100; i++) client.send("message-" + i);
        assertThat(server.receivedAll()).isTrue();           // all 100 arrive despite 30% loss
        assertThat(lossy.retransmits()).isGreaterThan(0);    // and retransmission actually happened
    }
}

@Test void udpNeverDeliversDuplicateOrOutOfOrder() throws Exception {
    assertThat(server.deliveryOrder()).isSorted();           // gaps are buffered, not skipped
}
```

## Deliverables

- [ ] Blocking TCP echo server with `SO_REUSEADDR`, `SO_TIMEOUT`, and `TCP_NODELAY`
- [ ] NIO selector server with per-connection output queues and no blocking writes
- [ ] Java 21 virtual thread server variant for high connection counts
- [ ] UDP protocol with SEQ/ACK header, windowing, cumulative ACK, and retransmit backoff
- [ ] Latency benchmark comparing blocking, NIO, and virtual thread servers
- [ ] A packet-loss-injecting test proving the UDP reliability layer recovers
- [ ] Tests: byte-order, concurrency, loss recovery, no duplicates or reordering
- [ ] README explaining when to choose each transport for your workload
