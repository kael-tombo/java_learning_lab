# THEORY — Networking Deep Dive

## Overview

Advanced Java networking: NIO.2 async I/O, HTTP/2 client, Netty patterns, gRPC, and performance tuning.

---

## NIO.2 Asynchronous I/O

### AsynchronousSocketChannel

```java
AsynchronousChannelGroup group = AsynchronousChannelGroup.withFixedThreadPool(
    Runtime.getRuntime().availableProcessors(), 
    Thread::new
);

AsynchronousSocketChannel channel = AsynchronousSocketChannel.open(group);
channel.connect(new InetSocketAddress("localhost", 8080), null, 
    new CompletionHandler<Void, Void>() {
        public void completed(Void result, Void attachment) {
            // Connected
            ByteBuffer buffer = ByteBuffer.wrap("GET / HTTP/1.1\r\n\r\n".getBytes());
            channel.write(buffer, null, new CompletionHandler<Integer, Void>() {
                public void completed(Integer result, Void attachment) {
                    // Write complete
                    ByteBuffer readBuffer = ByteBuffer.allocate(1024);
                    channel.read(readBuffer, null, new CompletionHandler<Integer, Void>() {
                        public void completed(Integer bytesRead, Void attachment) {
                            // Process response
                        }
                        public void failed(Throwable exc, Void attachment) { }
                    });
                }
                public void failed(Throwable exc, Void attachment) { }
            });
        }
        public void failed(Throwable exc, Void attachment) { }
    }
);
```

### AsynchronousServerSocketChannel

```java
AsynchronousServerSocketChannel server = AsynchronousServerSocketChannel.open()
    .bind(new InetSocketAddress(8080));

server.accept(null, new CompletionHandler<AsynchronousSocketChannel, Void>() {
    public void completed(AsynchronousSocketChannel client, Void attachment) {
        server.accept(null, this); // Accept next
        handleClient(client);
    }
    public void failed(Throwable exc, Void attachment) { }
});
```

---

## HTTP Client (Java 11+)

### Basic Usage

```java
HttpClient client = HttpClient.newBuilder()
    .version(HttpClient.Version.HTTP_2)
    .followRedirects(HttpClient.Redirect.NORMAL)
    .connectTimeout(Duration.ofSeconds(10))
    .build();

HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/users"))
    .header("Accept", "application/json")
    .header("Authorization", "Bearer " + token)
    .GET()
    .build();

// Synchronous
HttpResponse<String> response = client.send(request, BodyHandlers.ofString());

// Async
CompletableFuture<HttpResponse<String>> future = client.sendAsync(request, BodyHandlers.ofString());
future.thenAccept(resp -> process(resp.body()));
```

### Advanced Features

```java
// Request body
HttpRequest request = HttpRequest.newBuilder()
    .uri(URI.create("https://api.example.com/users"))
    .POST(BodyPublishers.ofString(json))
    .header("Content-Type", "application/json")
    .build();

// Streaming response
HttpResponse<InputStream> response = client.send(request, BodyHandlers.ofInputStream());
try (InputStream is = response.body()) {
    // Process stream
}

// WebSocket
HttpClient wsClient = HttpClient.newBuilder().build();
WebSocket ws = client.newWebSocketBuilder()
    .buildAsync(URI.create("wss://example.com/ws"), new WebSocket.Listener() {
        public void onText(WebSocket ws, CharSequence data, boolean last) {
            System.out.println("Received: " + data);
        }
        public void onError(WebSocket ws, Throwable error) { }
    }).join();

ws.sendText("Hello", true);
ws.sendClose(WebSocket.NORMAL_CLOSURE, "bye").join();
```

### Configuration

```java
HttpClient client = HttpClient.newBuilder()
    .version(HttpClient.Version.HTTP_2)
    .followRedirects(HttpClient.Redirect.NORMAL)
    .cookieHandler(CookieHandler.getDefault())
    .proxy(ProxySelector.of(new InetSocketAddress("proxy", 8080)))
    .authenticator(new Authenticator() {
        protected PasswordAuthentication getPasswordAuthentication() {
            return new PasswordAuthentication("user", "pass".toCharArray());
        }
    })
    .sslContext(SSLContext.getDefault())
    .sslParameters(new SSLParameters())
    .connectTimeout(Duration.ofSeconds(30))
    .build();
```

---

## Netty (High-Performance Networking)

### Server Bootstrap

```java
EventLoopGroup bossGroup = new NioEventLoopGroup(1);
EventLoopGroup workerGroup = new NioEventLoopGroup();

try {
    ServerBootstrap b = new ServerBootstrap();
    b.group(bossGroup, workerGroup)
     .channel(NioServerSocketChannel.class)
     .childHandler(new ChannelInitializer<SocketChannel>() {
         @Override
         protected void initChannel(SocketChannel ch) {
             ch.pipeline().addLast(
                 new HttpServerCodec(),
                 new HttpObjectAggregator(65536),
                 new MyHandler()
             );
         }
     })
     .option(ChannelOption.SO_BACKLOG, 128)
     .childOption(ChannelOption.SO_KEEPALIVE, true);

    ChannelFuture f = b.bind(8080).sync();
    f.channel().closeFuture().sync();
} finally {
    workerGroup.shutdownGracefully();
    bossGroup.shutdownGracefully();
}
```

### Handler

```java
public class MyHandler extends SimpleChannelInboundHandler<FullHttpRequest> {
    @Override
    protected void channelRead0(ChannelHandlerContext ctx, FullHttpRequest req) {
        if (req.uri().equals("/health")) {
            FullHttpResponse res = new DefaultFullHttpResponse(
                HTTP_1_1, OK, Unpooled.copiedBuffer("OK", UTF_8)
            );
            res.headers().set(CONTENT_TYPE, "text/plain");
            ctx.writeAndFlush(res);
        }
    }
}
```

### Pipeline Patterns

```
Inbound:  [Codec] → [Aggregator] → [Business Logic] → [Response]
Outbound: [Encoder] → [Compressor] → [SSL] → [Socket]
```

---

## gRPC

### Proto Definition

```protobuf
syntax = "proto3";

service UserService {
    rpc GetUser(GetUserRequest) returns (User);
    rpc ListUsers(ListUsersRequest) returns (stream User);
    rpc CreateUser(stream CreateUserRequest) returns (CreateUserResponse);
    rpc Chat(stream Message) returns (stream Message);
}

message User { string id = 1; string name = 2; string email = 3; }
```

### Server

```java
public class UserServiceImpl extends UserServiceGrpc.UserServiceImplBase {
    @Override
    public void getUser(GetUserRequest req, StreamObserver<User> responseObserver) {
        User user = userService.findById(req.getId());
        responseObserver.onNext(user);
        responseObserver.onCompleted();
    }

    @Override
    public StreamObserver<CreateUserRequest> createUser(StreamObserver<CreateUserResponse> responseObserver) {
        return new StreamObserver<>() {
            List<User> batch = new ArrayList<>();
            public void onNext(CreateUserRequest req) { batch.add(toUser(req)); }
            public void onError(Throwable t) { }
            public void onCompleted() {
                userService.saveAll(batch);
                responseObserver.onNext(CreateUserResponse.newBuilder().setCount(batch.size()).build());
                responseObserver.onCompleted();
            }
        };
    }
}

Server server = ServerBuilder.forPort(9090)
    .addService(new UserServiceImpl())
    .build()
    .start();
```

### Client

```java
ManagedChannel channel = ManagedChannelBuilder.forAddress("localhost", 9090)
    .usePlaintext()
    .build();

UserServiceGrpc.UserServiceBlockingStub blockingStub = UserServiceGrpc.newBlockingStub(channel);
User user = blockingStub.getUser(GetUserRequest.newBuilder().setId("123").build());

UserServiceGrpc.UserServiceStub asyncStub = UserServiceGrpc.newStub(channel);
asyncStub.getUser(GetUserRequest.newBuilder().setId("123").build(), 
    new StreamObserver<User>() {
        public void onNext(User user) { System.out.println(user); }
        public void onError(Throwable t) { }
        public void onCompleted() { }
    }
);
```

---

## Performance Tuning

### TCP Settings

```bash
# Linux kernel tuning
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 15
```

### JVM Settings

```bash
# Network buffer sizes
-Djdk.net.epoll.enabled=true          # Linux epoll
-Dsun.nio.ch.bufSize=65536            # Direct buffer size

# HTTP client pool
-Djdk.httpclient.connectionPoolSize=200
-Djdk.httpclient.keepAliveDuration=30
```

### Netty Tuning

```java
b.option(ChannelOption.SO_RCVBUF, 256 * 1024)
 .option(ChannelOption.SO_SNDBUF, 256 * 1024)
 .option(ChannelOption.TCP_NODELAY, true)
 .childOption(ChannelOption.ALLOCATOR, PooledByteBufAllocator.DEFAULT);
```

---

## Security

### TLS Configuration

```java
SSLContext sslContext = SSLContext.getInstance("TLSv1.3");
sslContext.init(keyManagers, trustManagers, null);

SSLParameters sslParams = new SSLParameters();
sslParams.setProtocols(new String[]{"TLSv1.3", "TLSv1.2"});
sslParams.setCipherSuites(new String[]{
    "TLS_AES_256_GCM_SHA384",
    "TLS_CHACHA20_POLY1305_SHA256"
});

HttpClient client = HttpClient.newBuilder()
    .sslContext(sslContext)
    .sslParameters(sslParams)
    .build();
```

### Certificate Pinning

```java
TrustManager[] trustManagers = new TrustManager[]{
    new X509ExtendedTrustManager() {
        public void checkServerTrusted(X509Certificate[] chain, String authType, Socket socket) {
            // Verify certificate fingerprint
            String fingerprint = getFingerprint(chain[0]);
            if (!EXPECTED_FINGERPRINTS.contains(fingerprint)) {
                throw new CertificateException("Pinning failed");
            }
        }
        // ... other methods
    }
};
```