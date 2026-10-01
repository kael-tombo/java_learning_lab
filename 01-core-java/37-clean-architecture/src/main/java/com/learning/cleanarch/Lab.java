package com.learning.cleanarch;

import java.util.*;
import java.util.function.*;

public class Lab {

    public static void main(String[] args) {
        System.out.println("=== Clean Architecture Lab (Conceptual) ===\n");

        architectureLayers();
        dependencyRule();
        useCases();
        entities();
        interfaceAdapters();
    }

    static void architectureLayers() {
        System.out.println("--- Clean Architecture Layers ---");

        System.out.println("""
            Circle 1: Frameworks & Drivers (DB, Web, UI)
            Circle 2: Interface Adapters (Controllers, Presenters, Gateways)
            Circle 3: Application Business Rules (Use Cases, Interactors)
            Circle 4: Enterprise Business Rules (Entities, Value Objects)

            Dependency rule: dependencies point INWARD.
            Outer circles depend on inner circles. Never the reverse.""");
    }

    static void dependencyRule() {
        System.out.println("\n--- Dependency Inversion ---");

        // BAD: depends on concrete
        class BadService {
            // private MySQLDatabase db = new MySQLDatabase(); // VIOLATION
        }

        // GOOD: depends on abstraction
        interface Database { String query(String sql); }
        class MySQLDB implements Database { public String query(String s) { return "MySQL: " + s; } }
        class PostgresDB implements Database { public String query(String s) { return "Postgres: " + s; } }

        class Service {
            final Database db;
            Service(Database db) { this.db = db; }
            String findUser() { return db.query("SELECT * FROM users"); }
        }

        System.out.println("  MySQL: " + new Service(new MySQLDB()).findUser());
        System.out.println("  Postgres: " + new Service(new PostgresDB()).findUser());

        System.out.println("\n  Traditional: Controller -> Service -> Repository -> DB (concrete->concrete)");
        System.out.println("  Clean Arch:  Controller -> UseCase I/F -> UseCase Impl -> Entity (concrete->abstract)");
    }

    static void useCases() {
        System.out.println("\n--- Use Cases ---");

        record User(String id, String name, String email) {}
        record CreateInput(String name, String email) {}
        record CreateOutput(String id, String name, String email) {}

        interface UserRepo { User save(User u); Optional<User> findById(String id); }
        interface EmailSvc { void sendWelcome(User u); }

        class CreateUserUC {
            final UserRepo repo; final EmailSvc email;
            CreateUserUC(UserRepo r, EmailSvc e) { repo = r; email = e; }

            CreateOutput exec(CreateInput input) {
                if (input.email() == null || !input.email().contains("@"))
                    throw new IllegalArgumentException("Invalid email");
                var user = new User(UUID.randomUUID().toString(), input.name(), input.email());
                var saved = repo.save(user);
                email.sendWelcome(saved);
                System.out.println("    Created: " + saved.name() + " <" + saved.email() + ">");
                return new CreateOutput(saved.id(), saved.name(), saved.email());
            }
        }

        class InMemRepo implements UserRepo {
            final Map<String, User> s = new HashMap<>();
            public User save(User u) { s.put(u.id(), u); return u; }
            public Optional<User> findById(String id) { return Optional.ofNullable(s.get(id)); }
        }

        var uc = new CreateUserUC(new InMemRepo(), u -> System.out.println("    [EMAIL] Welcome " + u.name()));
        var out = uc.exec(new CreateInput("Alice", "alice@x.com"));
    }

    static void entities() {
        System.out.println("\n--- Entities (Domain Layer) ---");

        record OrderItem(String product, int qty, double price) {}

        class Order {
            final String id;
            final List<OrderItem> items = new ArrayList<>();
            String status = "PENDING";
            Order(String id) { this.id = id; }

            void addItem(OrderItem item) {
                if ("SHIPPED".equals(status)) throw new IllegalStateException("Order shipped");
                items.add(item);
            }
            double total() { return items.stream().mapToDouble(i -> i.qty() * i.price()).sum(); }
            void submit() {
                if (items.isEmpty()) throw new IllegalStateException("Empty order");
                status = "SUBMITTED";
            }
        }

        var o = new Order("order-1");
        o.addItem(new OrderItem("PROD-1", 2, 29.99));
        o.addItem(new OrderItem("PROD-2", 1, 99.99));
        o.submit();
        System.out.printf("  Order %s: status=%s total=$%.2f%n", o.id, o.status, o.total());

        System.out.println("\n  Entity vs Value Object:");
        System.out.println("  Entity: has identity (id), mutable (User, Order)");
        System.out.println("  Value Object: identified by attributes, immutable (Money, Address)");

        System.out.println("\n  Domain invariants:");
        for (var i : List.of("Order must have >= 1 item", "Email must be unique",
                "Quantity >= 0", "Cancelled orders can't ship"))
            System.out.println("  -> " + i);
    }

    static void interfaceAdapters() {
        System.out.println("\n--- Interface Adapters ---");

        record Request(String method, String path, String body) {}
        record Response(int status, String body) {}
        record CreateInput(String name, String email) {}
        record CreateOutput(String id, String name, String email) {}
        interface CreateUserUC { CreateOutput exec(CreateInput input); }

        class UserController {
            final CreateUserUC uc;
            UserController(CreateUserUC uc) { this.uc = uc; }

            Response handleCreate(Request r) {
                try {
                    String name = r.body().replaceAll(".*\"name\":\"([^\"]+)\".*", "$1");
                    String email = r.body().replaceAll(".*\"email\":\"([^\"]+)\".*", "$1");
                    var out = uc.exec(new CreateInput(name, email));
                    return new Response(201, "{\"id\":\"" + out.id() + "\",\"name\":\"" + out.name() + "\"}");
                } catch (IllegalArgumentException e) {
                    return new Response(400, "{\"error\":\"" + e.getMessage() + "\"}");
                }
            }
        }

        class RealUC implements CreateUserUC {
            public CreateOutput exec(CreateInput input) {
                return new CreateOutput(UUID.randomUUID().toString(), input.name(), input.email());
            }
        }

        var ctrl = new UserController(new RealUC() {
            @Override
            public CreateOutput exec(CreateInput input) {
                System.out.println("    Use case: creating " + input.name());
                return new CreateOutput(UUID.randomUUID().toString(), input.name(), input.email());
            }
        });
        var resp = ctrl.handleCreate(new Request("POST", "/api/users", "{\"name\":\"Bob\",\"email\":\"b@x.com\"}"));
        System.out.println("  Response: " + resp.status() + " " + resp.body());

        System.out.println("\n  Adapters: Controller, Presenter, Gateway, DTO, Mapper");

        System.out.println("\n  Benefits: testability, framework-independence, DB-independence,");
        System.out.println("  UI-independence, deferred decisions, parallel development.");

        System.out.println("\n  Screaming architecture: package structure should scream what the app does.");
        System.out.println("  GOOD: com.myapp.user.CreateUserUseCase");
        System.out.println("  BAD:  com.myapp.spring.jpa.controllers.UserController");
    }
}
