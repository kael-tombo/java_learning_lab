# Code Deep Dive — Deep Java Networking (networking-deep)

Annotated Java 17+ snippets for sockets, NIO/NIO.2, Netty, HTTP client, WebSocket. Paste into `src/main/java`.

## Snippet 1: TCP/UDP sockets

TCP provides reliable, ordered, connection-oriented communication, while UDP provides unreliable, unordered, connectionless communication. The snippet below demonstrates a TCP echo server/client and a UDP echo server/client using `java.net` sockets.

```java
// networking-deep snippet 1: TCP/UDP sockets
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;

public class TcpUdpSockets {
    public static void main(String[] args) throws Exception {
        // TCP echo
        try (ServerSocket server = new ServerSocket(0)) {
            int port = server.getLocalPort();
            Thread serverThread = new Thread(() -> {
                try (Socket s = server.accept()) {
                    BufferedReader in = new BufferedReader(new InputStreamReader(s.getInputStream()));
                    PrintWriter out = new PrintWriter(s.getOutputStream(), true);
                    String line = in.readLine();
                    out.println("Echo: " + line);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            });
            serverThread.start();

            try (Socket client = new Socket("localhost", port)) {
                PrintWriter out = new PrintWriter(client.getOutputStream(), true);
                BufferedReader in = new BufferedReader(new InputStreamReader(client.getInputStream()));
                out.println("Hello TCP");
                System.out.println("TCP response: " + in.readLine());
            }
            serverThread.join();
        }

        // UDP
        try (DatagramSocket udpServer = new DatagramSocket(0)) {
            int port = udpServer.getLocalPort();
            Thread udpThread = new Thread(() -> {
                try {
                    byte[] buf = new byte[256];
                    DatagramPacket packet = new DatagramPacket(buf, buf.length);
                    udpServer.receive(packet);
                    String msg = new String(packet.getData(), 0, packet.getLength());
                    System.out.println("UDP server received: " + msg);
                } catch (IOException e) {
                    e.printStackTrace();
                }
            });
            udpThread.start();

            try (DatagramSocket udpClient = new DatagramSocket()) {
                byte[] data = "Hello UDP".getBytes();
                DatagramPacket packet = new DatagramPacket(data, data.length,
                    InetAddress.getByName("localhost"), port);
                udpClient.send(packet);
            }
            udpThread.join();
        }
    }
}
```

Observed output:
```
TCP response: Echo: Hello TCP
UDP server received: Hello UDP
```

Pitfall: TCP sockets are stream-oriented with no message boundaries — a single `read()` may return partial data, and multiple `send()` calls may be coalesced. For message-oriented protocols, implement a framing layer (length-prefixed or delimiter-based). UDP packets may be lost, duplicated, or reordered; if you need reliability, you must implement it yourself or use TCP.

## Snippet 2: NIO selectors & channels

NIO (New I/O) provides non-blocking I/O with selectors that multiplex many channels on a single thread. This is the foundation of scalable network servers. The snippet below implements a simple NIO echo server using a `Selector` to handle multiple clients.

```java
// networking-deep snippet 2: NIO selectors & channels
import java.io.IOException;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SelectionKey;
import java.nio.channels.Selector;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.util.Iterator;
import java.util.Set;

public class NioSelector {
    public static void main(String[] args) throws Exception {
        Selector selector = Selector.open();
        ServerSocketChannel serverChannel = ServerSocketChannel.open();
        serverChannel.bind(new InetSocketAddress(0));
        serverChannel.configureBlocking(false);
        serverChannel.register(selector, SelectionKey.OP_ACCEPT);
        int port = serverChannel.socket().getLocalPort();

        Thread serverThread = new Thread(() -> {
            try {
                while (!Thread.interrupted()) {
                    selector.select();
                    Set<SelectionKey> keys = selector.selectedKeys();
                    Iterator<SelectionKey> it = keys.iterator();
                    while (it.hasNext()) {
                        SelectionKey key = it.next();
                        it.remove();
                        if (key.isAcceptable()) {
                            SocketChannel client = serverChannel.accept();
                            client.configureBlocking(false);
                            client.register(selector, SelectionKey.OP_READ);
                        } else if (key.isReadable()) {
                            SocketChannel client = (SocketChannel) key.channel();
                            ByteBuffer buf = ByteBuffer.allocate(256);
                            int read = client.read(buf);
                            if (read > 0) {
                                buf.flip();
                                byte[] data = new byte[buf.remaining()];
                                buf.get(data);
                                System.out.println("NIO server received: " + new String(data));
                            }
                        }
                    }
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
        });
        serverThread.start();

        try (SocketChannel client = SocketChannel.open(new InetSocketAddress("localhost", port))) {
            client.write(ByteBuffer.wrap("Hello NIO".getBytes()));
            Thread.sleep(500);
        }
        serverThread.interrupt();
    }
}
```

Observed output:
```
NIO server received: Hello NIO
```

Pitfall: NIO selectors require careful handling of the selected key set — failing to call `keyIterator.remove()` causes the same key to be returned on every `select()` call, resulting in a busy loop. Also, a common bug is not handling partial reads or writes; a single `read()` may not read the entire message, and a single `write()` may not write the entire buffer.

## Snippet 3: NIO.2 async channels

NIO.2 (introduced in JDK 7) adds asynchronous channel APIs that use callbacks or `Future` objects for non-blocking I/O. The snippet below demonstrates an asynchronous server socket channel and client socket channel.

```java
// networking-deep snippet 3: NIO.2 async channels
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.AsynchronousServerSocketChannel;
import java.nio.channels.AsynchronousSocketChannel;
import java.util.concurrent.Future;

public class Nio2Async {
    public static void main(String[] args) throws Exception {
        AsynchronousServerSocketChannel server = AsynchronousServerSocketChannel.open();
        server.bind(new InetSocketAddress(0));
        int port = ((InetSocketAddress) server.getLocalAddress()).getPort();

        Future<AsynchronousSocketChannel> acceptFuture = server.accept();

        try (AsynchronousSocketChannel client = AsynchronousSocketChannel.open()) {
            client.connect(new InetSocketAddress("localhost", port)).get();
            ByteBuffer buf = ByteBuffer.wrap("Hello Async".getBytes());
            client.write(buf).get();

            AsynchronousSocketChannel accepted = acceptFuture.get();
            ByteBuffer readBuf = ByteBuffer.allocate(256);
            int bytesRead = accepted.read(readBuf).get();
            readBuf.flip();
            byte[] data = new byte[readBuf.remaining()];
            readBuf.get(data);
            System.out.println("Async server received: " + new String(data));
        }
        server.close();
    }
}
```

Observed output:
```
Async server received: Hello Async
```

Pitfall: Asynchronous channels use a thread pool internally, and the default pool size is small. For high-concurrency applications, customize the thread pool with `AsynchronousChannelGroup.withFixedThreadPool()`. Also, mixing `Future.get()` (blocking) with async callbacks can lead to deadlocks if the callback thread pool is exhausted.

## Snippet 4: Netty pipeline

Netty is a popular asynchronous event-driven network application framework. It provides a pipeline-based architecture where handlers process inbound and outbound events. The snippet below shows a minimal Netty echo server.

**Requires `io.netty:netty-all`; not compiled in this repo.**

```java
// networking-deep snippet 4: Netty pipeline
// Requires io.netty:netty-all; not compiled in this repo
import io.netty.bootstrap.ServerBootstrap;
import io.netty.channel.ChannelFuture;
import io.netty.channel.ChannelHandlerContext;
import io.netty.channel.ChannelInboundHandlerAdapter;
import io.netty.channel.ChannelInitializer;
import io.netty.channel.EventLoopGroup;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.socket.SocketChannel;
import io.netty.channel.socket.nio.NioServerSocketChannel;

import java.net.InetSocketAddress;

public class NettyPipeline {
    public static void main(String[] args) throws Exception {
        EventLoopGroup bossGroup = new NioEventLoopGroup(1);
        EventLoopGroup workerGroup = new NioEventLoopGroup();
        try {
            ServerBootstrap b = new ServerBootstrap();
            b.group(bossGroup, workerGroup)
             .channel(NioServerSocketChannel.class)
             .childHandler(new ChannelInitializer<SocketChannel>() {
                 @Override
                 protected void initChannel(SocketChannel ch) {
                     ch.pipeline().addLast(new EchoHandler());
                 }
             });
            ChannelFuture f = b.bind(0).sync();
            System.out.println("Netty server started on port " +
                ((InetSocketAddress) f.channel().localAddress()).getPort());
            f.channel().closeFuture().sync();
        } finally {
            bossGroup.shutdownGracefully();
            workerGroup.shutdownGracefully();
        }
    }
}

class EchoHandler extends ChannelInboundHandlerAdapter {
    @Override
    public void channelRead(ChannelHandlerContext ctx, Object msg) {
        ctx.write(msg);
    }

    @Override
    public void channelReadComplete(ChannelHandlerContext ctx) {
        ctx.flush();
    }

    @Override
    public void exceptionCaught(ChannelHandlerContext ctx, Throwable cause) {
        cause.printStackTrace();
        ctx.close();
    }
}
```

Pitfall: Netty's `ByteBuf` uses reference counting — failing to call `ReferenceCountUtil.release(msg)` after processing causes memory leaks. Also, never perform blocking operations in an event loop thread; use a separate business thread pool or the channel's `executor()`.

## Snippet 5: Java HttpClient

The `java.net.http.HttpClient` (JEP 321, final in JDK 11) is a modern HTTP client supporting HTTP/1.1, HTTP/2, and WebSocket. The snippet below starts a `com.sun.net.httpserver.HttpServer` (JEP 408, final in JDK 18) and sends a request to it.

```java
// networking-deep snippet 5: Java HttpClient
import com.sun.net.httpserver.HttpServer;
import java.net.InetSocketAddress;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class JavaHttpClient {
    public static void main(String[] args) throws Exception {
        HttpServer server = HttpServer.create(new InetSocketAddress(0), 0);
        server.createContext("/hello", exchange -> {
            String response = "Hello from HttpServer";
            exchange.sendResponseHeaders(200, response.length());
            exchange.getResponseBody().write(response.getBytes());
            exchange.close();
        });
        server.start();
        int port = server.getAddress().getPort();

        HttpClient client = HttpClient.newHttpClient();
        HttpRequest request = HttpRequest.newBuilder()
            .uri(URI.create("http://localhost:" + port + "/hello"))
            .build();
        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        System.out.println("Status: " + response.statusCode());
        System.out.println("Body: " + response.body());
        server.stop(0);
    }
}
```

Observed output:
```
Status: 200
Body: Hello from HttpServer
```

Pitfall: `HttpClient.send()` is blocking — for async operations, use `sendAsync()` which returns a `CompletableFuture`. Also, the default `HttpClient` does not follow redirects automatically; configure with `.redirect(HttpClient.Redirect.NORMAL)` if needed. The `HttpServer` in `com.sun.net.httpserver` is designed for testing and development, not production use.

## Snippet 6: WebSocket

WebSocket provides full-duplex communication over a single TCP connection. The JDK includes `java.net.http.WebSocket` (JEP 321) for client-side WebSocket. The snippet below implements a minimal WebSocket server that handles the upgrade handshake and echoes text messages.

```java
// networking-deep snippet 6: WebSocket
import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.WebSocket;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Base64;
import java.util.concurrent.CompletionStage;

public class WebSocketDemo {
    static void handleWebSocket(Socket socket) throws Exception {
        InputStream in = socket.getInputStream();
        OutputStream out = socket.getOutputStream();

        ByteArrayOutputStream headerBuf = new ByteArrayOutputStream();
        int prev = 0, cur;
        while ((cur = in.read()) != -1) {
            headerBuf.write(cur);
            if (prev == '\r' && cur == '\n') {
                byte[] h = headerBuf.toByteArray();
                if (h.length >= 4 && h[h.length - 4] == '\r' && h[h.length - 3] == '\n'
                    && h[h.length - 2] == '\r' && h[h.length - 1] == '\n') break;
            }
            prev = cur;
        }
        String headers = headerBuf.toString(StandardCharsets.UTF_8);
        String key = null;
        for (String line : headers.split("\r\n")) {
            if (line.startsWith("Sec-WebSocket-Key: ")) {
                key = line.substring(19).trim();
            }
        }

        String magic = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11";
        MessageDigest md = MessageDigest.getInstance("SHA-1");
        byte[] hash = md.digest((key + magic).getBytes(StandardCharsets.UTF_8));
        String accept = Base64.getEncoder().encodeToString(hash);

        String response = "HTTP/1.1 101 Switching Protocols\r\n" +
                          "Upgrade: websocket\r\n" +
                          "Connection: Upgrade\r\n" +
                          "Sec-WebSocket-Accept: " + accept + "\r\n\r\n";
        out.write(response.getBytes(StandardCharsets.UTF_8));
        out.flush();

        int b1 = in.read();
        int b2 = in.read();
        boolean masked = (b2 & 0x80) != 0;
        int len = b2 & 0x7F;
        byte[] mask = new byte[4];
        if (masked) {
            for (int i = 0; i < 4; i++) mask[i] = (byte) in.read();
        }
        byte[] data = new byte[len];
        for (int i = 0; i < len; i++) {
            data[i] = (byte) (in.read() ^ mask[i % 4]);
        }
        String msg = new String(data, StandardCharsets.UTF_8);
        System.out.println("WebSocket server received: " + msg);

        byte[] resp = ("Echo: " + msg).getBytes(StandardCharsets.UTF_8);
        out.write(0x81);
        out.write(resp.length);
        out.write(resp);
        out.flush();
    }

    public static void main(String[] args) throws Exception {
        try (ServerSocket server = new ServerSocket(0)) {
            int port = server.getLocalPort();
            Thread serverThread = new Thread(() -> {
                try {
                    Socket socket = server.accept();
                    handleWebSocket(socket);
                } catch (Exception e) {
                    e.printStackTrace();
                }
            });
            serverThread.start();

            HttpClient client = HttpClient.newHttpClient();
            WebSocket ws = client.newWebSocketBuilder()
                .buildAsync(URI.create("ws://localhost:" + port + "/"),
                    new WebSocket.Listener() {
                        @Override
                        public CompletionStage<?> onText(WebSocket webSocket, CharSequence data, boolean last) {
                            System.out.println("WebSocket client received: " + data);
                            return null;
                        }
                    }).get();
            ws.sendText("Hello WebSocket", true).get();
            Thread.sleep(500);
            ws.sendClose(WebSocket.NORMAL_CLOSURE, "done").get();
            serverThread.join();
        }
    }
}
```

Observed output:
```
WebSocket server received: Hello WebSocket
WebSocket client received: Echo: Hello WebSocket
```

Pitfall: WebSocket frames can be fragmented, and the simple server above handles only single-frame text messages. For production use, implement proper frame reassembly, ping/pong keepalive, and binary frame support. Also, WebSocket connections can be dropped by proxies or firewalls that have idle timeouts — implement application-level ping/pong to keep the connection alive.
