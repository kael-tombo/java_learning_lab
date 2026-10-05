# Mini Project — Deep Java Networking (networking-deep)

Build in 2–4h: small app exercising sockets, NIO/NIO.2, Netty, HTTP client, gRPC.

## Goal
A CLI/demo app that uses at least 4 of: TCP/UDP sockets, NIO selectors & channels, NIO.2 async channels, Netty pipeline.

## Requirements
- [ ] Use `TCP/UDP sockets` with a visible behavior/test.
- [ ] Use `NIO selectors & channels` with a visible behavior/test.
- [ ] Use `NIO.2 async channels` with a visible behavior/test.
- [ ] Use `Netty pipeline` with a visible behavior/test.
- [ ] Use `Java HttpClient` with a visible behavior/test.
- [ ] Use `WebSocket` with a visible behavior/test.
- [ ] 3+ JUnit tests green.
- [ ] README with run + sample output.

## Steps
1. Scaffold Maven module.
2. Implement core loop.
3. Add tests + one metric (time/heap/threads).
4. Demo script (5 min).

## Starter sketch
```java
// networking-deep mini: combine TCP/UDP sockets + NIO selectors & channels
public class MiniApp {
  public static void main(String[] a) { System.out.println("mini running"); }
}
```

## Rubric (10)
- Functionality 4, tests 2, clarity 2, metric 2.
Stretch 0: add TCP/UDP sockets variant.
Stretch 1: add NIO selectors & channels variant.
Stretch 2: add NIO.2 async channels variant.
Stretch 3: add Netty pipeline variant.
Stretch 4: add Java HttpClient variant.
Stretch 5: add WebSocket variant.
Stretch 6: add gRPC stubs variant.
Stretch 7: add backpressure over network variant.
Stretch 8: add TCP/UDP sockets variant.
Stretch 9: add NIO selectors & channels variant.
Stretch 10: add NIO.2 async channels variant.
Stretch 11: add Netty pipeline variant.
Stretch 12: add Java HttpClient variant.
Stretch 13: add WebSocket variant.
Stretch 14: add gRPC stubs variant.
Stretch 15: add backpressure over network variant.
Stretch 16: add TCP/UDP sockets variant.
Stretch 17: add NIO selectors & channels variant.
Stretch 18: add NIO.2 async channels variant.
Stretch 19: add Netty pipeline variant.
Stretch 20: add Java HttpClient variant.
Stretch 21: add WebSocket variant.
Stretch 22: add gRPC stubs variant.
Stretch 23: add backpressure over network variant.
Stretch 24: add TCP/UDP sockets variant.
Stretch 25: add NIO selectors & channels variant.
Stretch 26: add NIO.2 async channels variant.
Stretch 27: add Netty pipeline variant.
Stretch 28: add Java HttpClient variant.
Stretch 29: add WebSocket variant.
Stretch 30: add gRPC stubs variant.
Stretch 31: add backpressure over network variant.
Stretch 32: add TCP/UDP sockets variant.
Stretch 33: add NIO selectors & channels variant.
Stretch 34: add NIO.2 async channels variant.
Stretch 35: add Netty pipeline variant.
Stretch 36: add Java HttpClient variant.
Stretch 37: add WebSocket variant.
Stretch 38: add gRPC stubs variant.
Stretch 39: add backpressure over network variant.
Stretch 40: add TCP/UDP sockets variant.
Stretch 41: add NIO selectors & channels variant.
Stretch 42: add NIO.2 async channels variant.
Stretch 43: add Netty pipeline variant.
Stretch 44: add Java HttpClient variant.
Stretch 45: add WebSocket variant.
Stretch 46: add gRPC stubs variant.
Stretch 47: add backpressure over network variant.
Stretch 48: add TCP/UDP sockets variant.
Stretch 49: add NIO selectors & channels variant.
Stretch 50: add NIO.2 async channels variant.
Stretch 51: add Netty pipeline variant.
Stretch 52: add Java HttpClient variant.
Stretch 53: add WebSocket variant.
Stretch 54: add gRPC stubs variant.
Stretch 55: add backpressure over network variant.
Stretch 56: add TCP/UDP sockets variant.
