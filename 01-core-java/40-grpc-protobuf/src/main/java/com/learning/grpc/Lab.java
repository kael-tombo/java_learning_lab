package com.learning.grpc;

import java.io.*;
import java.util.*;
import java.util.concurrent.*;

public class Lab {

    static class ProtoMessage {
        final Map<Integer, Object> fields = new LinkedHashMap<>();

        ProtoMessage set(int fieldNumber, Object value) {
            fields.put(fieldNumber, value);
            return this;
        }

        byte[] encode() throws IOException {
            var baos = new ByteArrayOutputStream();
            var dos = new DataOutputStream(baos);
            for (var entry : fields.entrySet()) {
                dos.writeByte(entry.getKey());
                var val = entry.getValue();
                if (val instanceof String s) {
                    dos.writeByte(0);
                    dos.writeUTF(s);
                } else if (val instanceof Integer i) {
                    dos.writeByte(1);
                    dos.writeInt(i);
                } else if (val instanceof Long l) {
                    dos.writeByte(2);
                    dos.writeLong(l);
                } else if (val instanceof Boolean b) {
                    dos.writeByte(3);
                    dos.writeBoolean(b);
                } else if (val instanceof Double d) {
                    dos.writeByte(4);
                    dos.writeDouble(d);
                }
            }
            return baos.toByteArray();
        }

        static ProtoMessage decode(byte[] data) throws IOException {
            var msg = new ProtoMessage();
            var dis = new DataInputStream(new ByteArrayInputStream(data));
            while (dis.available() > 0) {
                int fieldNum = dis.readByte();
                int typeTag = dis.readByte();
                var val = switch (typeTag) {
                    case 0 -> dis.readUTF();
                    case 1 -> dis.readInt();
                    case 2 -> dis.readLong();
                    case 3 -> dis.readBoolean();
                    default -> dis.readDouble();
                };
                msg.fields.put(fieldNum, val);
            }
            return msg;
        }
    }

    static class UserService {
        private final Map<Integer, String> users = new ConcurrentHashMap<>();

        String getUser(int id) {
            return users.getOrDefault(id, "User" + id);
        }

        String createUser(int id, String name) {
            users.put(id, name);
            return "Created: " + name;
        }

        String listUsers() {
            var sb = new StringBuilder();
            users.forEach((k, v) -> sb.append("[" + k + ":" + v + "] "));
            return sb.toString();
        }
    }

    public static void main(String[] args) throws Exception {
        System.out.println("=== gRPC & Protobuf Lab ===\n");

        protobufSerialization();
        serviceDefinition();
        unaryRpc();
        serverStreaming();
        clientStreaming();
        bidirectionalStreaming();
    }

    static void protobufSerialization() throws Exception {
        System.out.println("--- Protobuf-like Serialization ---");

        var original = new ProtoMessage()
            .set(1, "Alice")
            .set(2, 30)
            .set(3, true);

        System.out.println("  Original fields: " + original.fields);

        var bytes = original.encode();
        System.out.println("  Encoded: " + bytes.length + " bytes");

        var decoded = ProtoMessage.decode(bytes);
        System.out.println("  Decoded fields: " + decoded.fields);
        System.out.println("  Match: " + original.fields.equals(decoded.fields));
    }

    static void serviceDefinition() {
        System.out.println("\n--- Service Definition (.proto equivalent) ---");
        System.out.println("""
  service UserService {
    rpc GetUser (GetUserRequest) returns (GetUserResponse);
    rpc CreateUser (CreateUserRequest) returns (CreateUserResponse);
    rpc ListUsers (Empty) returns (stream User);
  }
  message GetUserRequest { int32 id = 1; }
  message GetUserResponse { string name = 1; int32 age = 2; }
  """);
        System.out.println("  gRPC uses HTTP/2, Protocol Buffers, stub generation");
        System.out.println("  Service = interface, Stub = client, Server = implementation");
    }

    static void unaryRpc() {
        System.out.println("\n--- Unary RPC ---");
        var service = new UserService();
        System.out.println("  " + service.createUser(1, "Alice"));
        System.out.println("  " + service.createUser(2, "Bob"));
        System.out.println("  " + service.getUser(1));
    }

    static void serverStreaming() {
        System.out.println("\n--- Server Streaming ---");
        var service = new UserService();
        service.createUser(1, "Alice");
        service.createUser(2, "Bob");
        service.createUser(3, "Carol");

        String result = service.listUsers();
        System.out.println("  Server streams: " + result);
        System.out.println("  gRPC: server pushes multiple responses for one request");
    }

    static void clientStreaming() {
        System.out.println("\n--- Client Streaming ---");
        var received = new ArrayList<String>();
        received.add("Request-1: CREATE id=4 name=Diana");
        received.add("Request-2: CREATE id=5 name=Eve");
        received.add("Request-3: LIST");

        System.out.println("  Client sends batch of messages:");
        received.forEach(s -> System.out.println("    " + s));
        System.out.println("  Server returns aggregate response after stream ends");
    }

    static void bidirectionalStreaming() {
        System.out.println("\n--- Bidirectional Streaming ---");
        System.out.println("  Both sides send independent streams of messages");
        System.out.println("  Order preserved within each stream, not across");
        System.out.println("  Use cases: chat, real-time collaboration, telemetry");
        System.out.println("  gRPC: async, non-blocking, HTTP/2 multiplexed streams");
    }
}
