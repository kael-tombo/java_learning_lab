# Code Examples — Processing a List of Orders Across Java Versions

> This file shows the SAME problem solved in each major Java version using the features available at the time.

---

## The Problem

We have a list of orders. Each order has:
- An ID
- A customer name
- A list of line items (each with product name, quantity, price)
- A status (PENDING, PROCESSING, SHIPPED, DELIVERED, CANCELLED)

We want to:
1. Filter orders to only PENDING or PROCESSING
2. For each order, compute the total value
3. Format the result as: `"Order <id> for <customer>: $<total> — <status>"`
4. Filter out orders with total value less than $10
5. Sort by total value (highest first)
6. Output the top 5 results

---

## Java 5 (Tiger) — Generics, For-Each, Autoboxing

```java
import java.util.*;

public class OrderProcessor {
    
    static class Order {
        private final int id;
        private final String customer;
        private final List<LineItem> items;
        private final String status;
        
        public Order(int id, String customer, List<LineItem> items, String status) {
            this.id = id;
            this.customer = customer;
            this.items = items;
            this.status = status;
        }
        
        public int getId() { return id; }
        public String getCustomer() { return customer; }
        public List<LineItem> getItems() { return items; }
        public String getStatus() { return status; }
        
        public double getTotal() {
            double total = 0.0;
            for (LineItem item : items) {
                total += item.getQuantity() * item.getPrice();
            }
            return total;
        }
    }
    
    static class LineItem {
        private final String product;
        private final int quantity;
        private final double price;
        
        public LineItem(String product, int quantity, double price) {
            this.product = product;
            this.quantity = quantity;
            this.price = price;
        }
        
        public String getProduct() { return product; }
        public int getQuantity() { return quantity; }
        public double getPrice() { return price; }
    }
    
    public static void main(String[] args) {
        List<Order> orders = Arrays.asList(
            new Order(1, "Alice", Arrays.asList(
                new LineItem("Widget", 3, 5.0),
                new LineItem("Gadget", 1, 25.0)
            ), "PENDING"),
            new Order(2, "Bob", Arrays.asList(
                new LineItem("Thingamajig", 2, 3.0)
            ), "SHIPPED"),
            new Order(3, "Charlie", Arrays.asList(
                new LineItem("Doohickey", 5, 10.0)
            ), "PROCESSING"),
            new Order(4, "Diana", Arrays.asList(
                new LineItem("Widget", 1, 5.0)
            ), "PENDING"),
            new Order(5, "Eve", Arrays.asList(
                new LineItem("Gadget", 10, 2.5)
            ), "DELIVERED"),
            new Order(6, "Frank", Arrays.asList(
                new LineItem("Thingamajig", 4, 12.0),
                new LineItem("Doohickey", 2, 8.0)
            ), "PROCESSING"),
            new Order(7, "Grace", Arrays.asList(
                new LineItem("Widget", 2, 15.0)
            ), "PENDING"),
            new Order(8, "Hank", Arrays.asList(
                new LineItem("Gadget", 1, 3.5)
            ), "CANCELLED"),
            new Order(9, "Ivy", Arrays.asList(
                new LineItem("Doohickey", 3, 6.0),
                new LineItem("Thingamajig", 1, 20.0)
            ), "PENDING"),
            new Order(10, "Jack", Arrays.asList(
                new LineItem("Widget", 1, 2.0)
            ), "PROCESSING")
        );
        
        // Step 1: Filter PENDING or PROCESSING
        List<Order> filtered = new ArrayList<Order>();
        for (Order order : orders) {
            String status = order.getStatus();
            if (status.equals("PENDING") || status.equals("PROCESSING")) {
                filtered.add(order);
            }
        }
        
        // Step 2: Build result strings with total
        List<String> results = new ArrayList<String>();
        for (Order order : filtered) {
            double total = order.getTotal();
            if (total >= 10.0) {
                results.add(String.format(
                    "Order %d for %s: $%.2f — %s",
                    order.getId(), order.getCustomer(), total, order.getStatus()
                ));
            }
        }
        
        // Step 3: Sort by total value (highest first)
        // Need to extract total again — no elegant way without map
        Collections.sort(results, new Comparator<String>() {
            public int compare(String a, String b) {
                double totalA = extractTotal(a);
                double totalB = extractTotal(b);
                if (totalA > totalB) return -1;
                if (totalA < totalB) return 1;
                return 0;
            }
        });
        
        // Step 4: Top 5
        int limit = Math.min(5, results.size());
        for (int i = 0; i < limit; i++) {
            System.out.println(results.get(i));
        }
    }
    
    private static double extractTotal(String formatted) {
        int dollarIndex = formatted.indexOf('$');
        int endIndex = formatted.indexOf(" —", dollarIndex);
        return Double.parseDouble(formatted.substring(dollarIndex + 1, endIndex));
    }
}
```

**Java 5 features demonstrated**: Generics (`List<Order>`), for-each loops, autoboxing (in Collections.sort comparator, implicit), varargs (String.format), annotations (@Override), enum (could be used for status but using String for simplicity).

---

## Java 7 — Diamond, Try-With-Resources, Multi-Catch

```java
import java.io.*;
import java.nio.file.*;
import java.util.*;

public class OrderProcessor {
    
    static class Order {
        private final int id;
        private final String customer;
        private final List<LineItem> items;
        private final String status;
        
        public Order(int id, String customer, List<LineItem> items, String status) {
            this.id = id;
            this.customer = customer;
            this.items = items;
            this.status = status;
        }
        
        public int getId() { return id; }
        public String getCustomer() { return customer; }
        public List<LineItem> getItems() { return items; }
        public String getStatus() { return status; }
        
        public double getTotal() {
            double total = 0.0;
            for (LineItem item : items) {
                total += item.getQuantity() * item.getPrice();
            }
            return total;
        }
    }
    
    static class LineItem {
        private final String product;
        private final int quantity;
        private final double price;
        
        public LineItem(String product, int quantity, double price) {
            this.product = product;
            this.quantity = quantity;
            this.price = price;
        }
        
        public String getProduct() { return product; }
        public int getQuantity() { return quantity; }
        public double getPrice() { return price; }
    }
    
    public static void main(String[] args) {
        // Diamond operator
        List<Order> orders = new ArrayList<>();
        // ... (same data as Java 5 example) ...
        
        // Reading from file with try-with-resources (new in 7)
        Path inputPath = Paths.get("orders.txt");
        if (Files.exists(inputPath)) {
            try (BufferedReader reader = Files.newBufferedReader(inputPath)) {
                String line;
                while ((line = reader.readLine()) != null) {
                    // parse orders
                }
            } catch (IOException | RuntimeException e) { // multi-catch
                System.err.println("Error reading orders: " + e.getMessage());
            }
        }
        
        // Process (same logic as Java 5 but with diamond operator)
        List<Order> filtered = new ArrayList<>();
        for (Order order : orders) {
            String status = order.getStatus();
            if (status.equals("PENDING") || status.equals("PROCESSING")) {
                filtered.add(order);
            }
        }
        
        // Strings in switch (new in 7)
        List<Order> filtered2 = new ArrayList<>();
        for (Order order : orders) {
            switch (order.getStatus()) {
                case "PENDING":
                case "PROCESSING":
                    filtered2.add(order);
                    break;
                default:
                    // skip
            }
        }
        
        // Rest same as Java 5 (no streams yet)
    }
}
```

**Java 7 features demonstrated**: Diamond operator (`new ArrayList<>()`), try-with-resources (AutoCloseable), multi-catch (`IOException | RuntimeException`), strings in switch, `Paths`/`Files` (NIO.2).

---

## Java 8 — Lambdas, Streams, Optional, Method References

```java
import java.time.*;
import java.util.*;
import java.util.stream.*;

public class OrderProcessor {
    
    static class Order {
        private final int id;
        private final String customer;
        private final List<LineItem> items;
        private final String status;
        
        public Order(int id, String customer, List<LineItem> items, String status) {
            this.id = id;
            this.customer = customer;
            this.items = items;
            this.status = status;
        }
        
        public int getId() { return id; }
        public String getCustomer() { return customer; }
        public List<LineItem> getItems() { return items; }
        public String getStatus() { return status; }
        
        public double getTotal() {
            return items.stream()
                .mapToDouble(item -> item.getQuantity() * item.getPrice())
                .sum();
        }
    }
    
    static class LineItem {
        private final String product;
        private final int quantity;
        private final double price;
        
        public LineItem(String product, int quantity, double price) {
            this.product = product;
            this.quantity = quantity;
            this.price = price;
        }
        
        public String getProduct() { return product; }
        public int getQuantity() { return quantity; }
        public double getPrice() { return price; }
    }
    
    public static void main(String[] args) {
        List<Order> orders = Arrays.asList(
            new Order(1, "Alice", Arrays.asList(
                new LineItem("Widget", 3, 5.0),
                new LineItem("Gadget", 1, 25.0)
            ), "PENDING"),
            new Order(2, "Bob", Arrays.asList(
                new LineItem("Thingamajig", 2, 3.0)
            ), "SHIPPED"),
            new Order(3, "Charlie", Arrays.asList(
                new LineItem("Doohickey", 5, 10.0)
            ), "PROCESSING"),
            new Order(4, "Diana", Arrays.asList(
                new LineItem("Widget", 1, 5.0)
            ), "PENDING"),
            new Order(5, "Eve", Arrays.asList(
                new LineItem("Gadget", 10, 2.5)
            ), "DELIVERED"),
            new Order(6, "Frank", Arrays.asList(
                new LineItem("Thingamajig", 4, 12.0),
                new LineItem("Doohickey", 2, 8.0)
            ), "PROCESSING"),
            new Order(7, "Grace", Arrays.asList(
                new LineItem("Widget", 2, 15.0)
            ), "PENDING"),
            new Order(8, "Hank", Arrays.asList(
                new LineItem("Gadget", 1, 3.5)
            ), "CANCELLED"),
            new Order(9, "Ivy", Arrays.asList(
                new LineItem("Doohickey", 3, 6.0),
                new LineItem("Thingamajig", 1, 20.0)
            ), "PENDING"),
            new Order(10, "Jack", Arrays.asList(
                new LineItem("Widget", 1, 2.0)
            ), "PROCESSING")
        );
        
        // Elegant stream pipeline
        List<String> topOrders = orders.stream()
            .filter(o -> o.getStatus().equals("PENDING") || o.getStatus().equals("PROCESSING"))
            .filter(o -> o.getTotal() >= 10.0)
            .sorted(Comparator.comparingDouble(Order::getTotal).reversed())
            .limit(5)
            .map(o -> String.format(
                "Order %d for %s: $%.2f — %s",
                o.getId(), o.getCustomer(), o.getTotal(), o.getStatus()
            ))
            .collect(Collectors.toList());
        
        topOrders.forEach(System.out::println);
        
        // Optional example: find order by ID safely
        Optional<Order> found = orders.stream()
            .filter(o -> o.getId() == 3)
            .findFirst();
        
        // Optional pattern
        String result = found
            .map(o -> String.format("Found order %d for %s", o.getId(), o.getCustomer()))
            .orElse("Order not found");
        
        System.out.println(result);
        
        // Date/Time API
        LocalDate today = LocalDate.now();
        System.out.println("Processed on: " + today);
        
        // Parallel stream for large datasets
        List<String> parallelResult = orders.parallelStream()
            .filter(o -> o.getStatus().equals("PENDING"))
            .map(o -> o.getCustomer() + " (" + o.getId() + ")")
            .collect(Collectors.toList());
    }
}
```

**Java 8 features demonstrated**: Lambda expressions (`.stream().filter(o -> ...)`), Stream API (filter, sorted, map, limit, collect), method references (`Order::getTotal`, `System.out::println`), `Optional<T>` for null-safe handling, `LocalDate` from `java.time`, `Collectors.toList()`, `Comparator.comparingDouble`, parallel streams.

---

## Java 9 — List.of, Stream Improvements

```java
import java.util.*;
import java.util.stream.*;

public class OrderProcessor {
    
    // ... (same inner classes as Java 8) ...
    
    public static void main(String[] args) {
        // List.of() — immutable list (factory method)
        List<Order> orders = List.of(
            new Order(1, "Alice", List.of(
                new LineItem("Widget", 3, 5.0),
                new LineItem("Gadget", 1, 25.0)
            ), "PENDING"),
            new Order(2, "Bob", List.of(
                new LineItem("Thingamajig", 2, 3.0)
            ), "SHIPPED"),
            new Order(3, "Charlie", List.of(
                new LineItem("Doohickey", 5, 10.0)
            ), "PROCESSING")
            // ... more orders
        );
        
        // takeWhile — process while status is PENDING
        orders.stream()
            .takeWhile(o -> o.getStatus().equals("PENDING"))
            .forEach(o -> System.out.println("Pending: " + o.getId()));
        
        // dropWhile — skip PENDING, process the rest
        orders.stream()
            .dropWhile(o -> o.getStatus().equals("PENDING"))
            .forEach(o -> System.out.println("Non-pending: " + o.getId()));
        
        // ofNullable — avoid null streams
        Order maybeNull = null;
        Stream.ofNullable(maybeNull)
            .forEach(o -> System.out.println("Will not print"));
        
        // Optional.ifPresentOrElse (new in 9)
        findOrder(orders, 5).ifPresentOrElse(
            o -> System.out.println("Found: " + o.getCustomer()),
            () -> System.out.println("Order not found")
        );
        
        // Stream.iterate with predicate (new in 9)
        Stream.iterate(0, n -> n < 10, n -> n + 1)
            .forEach(System.out::println);
    }
    
    private static Optional<Order> findOrder(List<Order> orders, int id) {
        return orders.stream()
            .filter(o -> o.getId() == id)
            .findFirst();
    }
}
```

**Java 9 features demonstrated**: `List.of()`, `Set.of()`, `Map.of()` factory methods, `Stream.takeWhile`/`dropWhile`, `Stream.ofNullable`, `Optional.ifPresentOrElse`, `Stream.iterate` with predicate.

---

## Java 10 — var

```java
import java.util.*;
import java.util.stream.*;

public class OrderProcessor {
    
    public static void main(String[] args) {
        // var — local variable type inference
        var orders = List.of(
            new Order(1, "Alice", List.of(
                new LineItem("Widget", 3, 5.0)
            ), "PENDING")
        );
        
        // var with streams — cleaner
        var topOrders = orders.stream()
            .filter(o -> o.getStatus().equals("PENDING"))
            .filter(o -> o.getTotal() >= 10.0)
            .sorted(Comparator.comparingDouble(Order::getTotal).reversed())
            .limit(5)
            .map(o -> String.format(
                "Order %d for %s: $%.2f — %s",
                o.getId(), o.getCustomer(), o.getTotal(), o.getStatus()
            ))
            .collect(Collectors.toList());
        
        topOrders.forEach(System.out::println);
        
        // var with for-each
        for (var order : orders) {
            System.out.println(order.getCustomer());
        }
        
        // var in try-with-resources
        // try (var reader = Files.newBufferedReader(path)) { ... }
    }
}
```

**Java 10 features demonstrated**: `var` for local variables (stream pipeline, for-each loops, resource variables).

---

## Java 11 — Collection.toArray, Files.readString

```java
import java.io.IOException;
import java.net.http.*;
import java.net.URI;
import java.nio.file.*;
import java.util.*;
import java.util.stream.*;

public class OrderProcessor {
    
    public static void main(String[] args) throws IOException, InterruptedException {
        // Collection.toArray(String[]::new) — cleaner than toArray(new String[0])
        var orders = loadOrders();
        
        var orderSummaries = orders.stream()
            .filter(o -> o.getStatus().equals("PENDING"))
            .map(o -> o.getCustomer() + ":" + o.getTotal())
            .toArray(String[]::new);  // Java 11: method reference
        
        // Files.readString / Files.writeString — simplified text I/O
        var path = Files.createTempFile("orders", ".txt");
        Files.writeString(path, "Order data goes here");
        var content = Files.readString(path);
        System.out.println("Wrote: " + content);
        
        // HTTP Client (standard in Java 11)
        var client = HttpClient.newHttpClient();
        var request = HttpRequest.newBuilder()
            .uri(URI.create("https://api.orders.example.com/top"))
            .GET()
            .build();
        var response = client.send(request, HttpResponse.BodyHandlers.ofString());
        System.out.println("API response: " + response.statusCode());
        
        // String.isBlank, strip, repeat
        var blank = "   ";
        System.out.println(blank.isBlank());  // true
        System.out.println(blank.strip().isEmpty());  // true
        System.out.println("Ha".repeat(3));  // HaHaHa
        
        // Optional.isEmpty
        Optional<Order> maybeOrder = findOrder(orders, 99);
        System.out.println(maybeOrder.isEmpty());  // true
    }
}
```

**Java 11 features demonstrated**: `Collection.toArray(T[]::new)`, `Files.readString`/`Files.writeString`, `java.net.http.HttpClient`, `String.isBlank()`, `String.strip()`, `String.repeat()`, `Optional.isEmpty()`.

---

## Java 14 — Records for Order

```java
import java.util.*;
import java.util.stream.*;

// Records — auto-generates constructor, accessors, equals, hashCode, toString
public record LineItem(String product, int quantity, double price) {}

public record Order(int id, String customer, List<LineItem> items, String status) {
    
    // Compact constructor with validation
    public Order {
        if (id <= 0) throw new IllegalArgumentException("ID must be positive");
        if (customer == null || customer.isBlank()) throw new IllegalArgumentException("Customer required");
        if (items == null || items.isEmpty()) throw new IllegalArgumentException("Items required");
        if (status == null) throw new IllegalArgumentException("Status required");
    }
    
    // Instance method
    public double getTotal() {
        return items.stream()
            .mapToDouble(item -> item.quantity() * item.price())
            .sum();
    }
}

public class OrderProcessor {
    
    public static void main(String[] args) {
        var orders = List.of(
            new Order(1, "Alice", List.of(
                new LineItem("Widget", 3, 5.0),
                new LineItem("Gadget", 1, 25.0)
            ), "PENDING"),
            new Order(3, "Charlie", List.of(
                new LineItem("Doohickey", 5, 10.0)
            ), "PROCESSING")
        );
        
        // Record accessors: order.id(), order.customer()
        var top = orders.stream()
            .filter(o -> o.status().equals("PENDING") || o.status().equals("PROCESSING"))
            .filter(o -> o.getTotal() >= 10.0)
            .sorted(Comparator.comparingDouble(Order::getTotal).reversed())
            .limit(5)
            .map(o -> String.format(
                "Order %d for %s: $%.2f — %s",
                o.id(), o.customer(), o.getTotal(), o.status()
            ))
            .collect(Collectors.toList());
        
        top.forEach(System.out::println);
        
        // Record toString is meaningful
        var order = orders.get(0);
        System.out.println(order);
        // Output: Order[id=1, customer=Alice, items=[...], status=PENDING]
        
        // Records automatically support equals/hashCode
        var order1 = new Order(1, "Alice", List.of(new LineItem("A", 1, 10.0)), "PENDING");
        var order2 = new Order(1, "Alice", List.of(new LineItem("A", 1, 10.0)), "PENDING");
        System.out.println(order1.equals(order2));  // true
    }
}
```

**Java 14 features demonstrated**: Records (`record Order(...)`), compact constructor (validation without parameter list), auto-generated `equals`/`hashCode`/`toString`, record accessors (`order.id()` instead of `order.getId()`).

---

## Java 16 — Stream.toList(), Pattern Matching for instanceof

```java
import java.util.*;
import java.util.stream.*;

public record LineItem(String product, int quantity, double price) {}
public record Order(int id, String customer, List<LineItem> items, String status) {
    public double getTotal() {
        return items.stream()
            .mapToDouble(item -> item.quantity() * item.price())
            .sum();
    }
}

public class OrderProcessor {
    
    public static void main(String[] args) {
        var orders = List.of(
            new Order(1, "Alice", List.of(
                new LineItem("Widget", 3, 5.0),
                new LineItem("Gadget", 1, 25.0)
            ), "PENDING")
        );
        
        // Stream.toList() — returns immutable list directly
        var top = orders.stream()
            .filter(o -> o.status().equals("PENDING") || o.status().equals("PROCESSING"))
            .filter(o -> o.getTotal() >= 10.0)
            .sorted(Comparator.comparingDouble(Order::getTotal).reversed())
            .limit(5)
            .map(o -> String.format(
                "Order %d for %s: $%.2f — %s",
                o.id(), o.customer(), o.getTotal(), o.status()
            ))
            .toList();  // Java 16: simpler than collect(Collectors.toList())
        
        // Pattern matching for instanceof
        Object obj = orders.get(0);
        if (obj instanceof Order order) {
            System.out.println("Order for: " + order.customer());
            
            // Nested pattern matching
            if (!order.items().isEmpty()) {
                var item = order.items().get(0);
                if (item instanceof LineItem li) {
                    System.out.println("First product: " + li.product());
                }
            }
        }
    }
}
```

**Java 16 features demonstrated**: `Stream.toList()` (simpler, returns immutable list), Pattern matching for `instanceof` (`obj instanceof Order order` — binding variable).

---

## Java 17 — Sealed Classes for OrderStatus, Pattern Matching Switch Preview

```java
import java.util.*;
import java.util.stream.*;

public record LineItem(String product, int quantity, double price) {}

// Sealed hierarchy for order status
public sealed interface OrderStatus 
    permits Pending, Processing, Shipped, Delivered, Cancelled {}

public record Pending() implements OrderStatus {}
public record Processing() implements OrderStatus {}
public record Shipped(String trackingNumber) implements OrderStatus {}
public record Delivered() implements OrderStatus {}
public record Cancelled(String reason) implements OrderStatus {}

// Order record uses the sealed type
public record Order(int id, String customer, List<LineItem> items, OrderStatus status) {
    public double getTotal() {
        return items.stream()
            .mapToDouble(item -> item.quantity() * item.price())
            .sum();
    }
}

public class OrderProcessor {
    
    // Pattern matching for switch (preview in 17, stable in 21)
    public static String describeStatus(OrderStatus status) {
        return switch (status) {
            case Pending p -> "Pending";
            case Processing p -> "Processing";
            case Shipped s -> "Shipped (tracking: " + s.trackingNumber() + ")";
            case Delivered d -> "Delivered";
            case Cancelled c -> "Cancelled: " + c.reason();
            // No default needed — sealed hierarchy is exhaustive
        };
    }
    
    public static void main(String[] args) {
        var orders = List.of(
            new Order(1, "Alice", List.of(
                new LineItem("Widget", 3, 5.0),
                new LineItem("Gadget", 1, 25.0)
            ), new Pending()),
            new Order(3, "Charlie", List.of(
                new LineItem("Doohickey", 5, 10.0)
            ), new Processing())
        );
        
        var top = orders.stream()
            .filter(o -> o.status() instanceof Pending || o.status() instanceof Processing)
            .filter(o -> o.getTotal() >= 10.0)
            .sorted(Comparator.comparingDouble(Order::getTotal).reversed())
            .limit(5)
            .map(o -> String.format(
                "Order %d for %s: $%.2f — %s",
                o.id(), o.customer(), o.getTotal(), describeStatus(o.status())
            ))
            .toList();
        
        top.forEach(System.out::println);
    }
}
```

**Java 17 features demonstrated**: Sealed classes/interfaces (`sealed interface OrderStatus permits ...`), record subtypes for sealed hierarchy, pattern matching for switch (preview).

---

## Java 21 — Pattern Matching for Switch, Record Patterns, Virtual Threads

```java
import java.time.Duration;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;

// Sealed status hierarchy
public sealed interface OrderStatus 
    permits Pending, Processing, Shipped, Delivered, Cancelled {}
public record Pending() implements OrderStatus {}
public record Processing() implements OrderStatus {}
public record Shipped(String trackingNumber) implements OrderStatus {}
public record Delivered() implements OrderStatus {}
public record Cancelled(String reason) implements OrderStatus {}

// Order record
public record Order(int id, String customer, List<LineItem> items, OrderStatus status) {
    public double getTotal() {
        return items.stream()
            .mapToDouble(item -> item.quantity() * item.price())
            .sum();
    }
}

public record LineItem(String product, int quantity, double price) {}

public class OrderProcessor {
    
    // Pattern matching for switch — finalized
    public static String describeStatus(OrderStatus status) {
        return switch (status) {
            case Pending p -> "Pending";
            case Processing p -> "Processing";
            case Shipped(var tracking) -> "Shipped (tracking: " + tracking + ")";  // record pattern
            case Delivered d -> "Delivered";
            case Cancelled(var reason) -> "Cancelled: " + reason;  // record pattern deconstruction
        };
    }
    
    // Record pattern in instanceof
    public static void printOrderDetails(Object obj) {
        if (obj instanceof Order(int id, String customer, _, _)) {  // unnamed pattern for ignored components
            System.out.println("Order #" + id + " for " + customer);
        }
    }
    
    // Virtual thread processing
    public static void processOrdersConcurrently(List<Order> orders) throws Exception {
        try (var executor = Executors.newVirtualThreadPerTaskExecutor()) {
            var futures = orders.stream()
                .filter(o -> o.status() instanceof Pending || o.status() instanceof Processing)
                .map(o -> executor.submit(() -> {
                    // Simulate processing — I/O bound (virtual threads shine here)
                    Thread.sleep(Duration.ofMillis(10));
                    return String.format(
                        "Order %d for %s: $%.2f — %s",
                        o.id(), o.customer(), o.getTotal(), describeStatus(o.status())
                    );
                }))
                .toList();
            
            for (var future : futures) {
                System.out.println(future.get());
            }
        }  // close() waits for all virtual threads
    }
    
    public static void main(String[] args) throws Exception {
        var orders = List.of(
            new Order(1, "Alice", List.of(
                new LineItem("Widget", 3, 5.0),
                new LineItem("Gadget", 1, 25.0)
            ), new Pending()),
            new Order(3, "Charlie", List.of(
                new LineItem("Doohickey", 5, 10.0)
            ), new Processing()),
            new Order(7, "Grace", List.of(
                new LineItem("Widget", 2, 15.0)
            ), new Pending()),
            new Order(9, "Ivy", List.of(
                new LineItem("Doohickey", 3, 6.0),
                new LineItem("Thingamajig", 1, 20.0)
            ), new Pending()),
            new Order(10, "Jack", List.of(
                new LineItem("Widget", 1, 2.0)
            ), new Processing())
        );
        
        // Sequenced collection: getFirst, getLast, reversed
        System.out.println("First order: " + orders.getFirst().customer());
        System.out.println("Last order: " + orders.getLast().customer());
        
        // Process concurrently with virtual threads
        processOrdersConcurrently(orders);
        
        // Pattern matching with guard
        var highValuePending = orders.stream()
            .filter(o -> o.status() instanceof Pending && o.getTotal() >= 50.0)
            .toList();
        
        // Exhaustive switch with pattern matching
        for (var order : orders) {
            var description = switch (order.status()) {
                case Pending p -> "Needs processing";
                case Processing p -> "Currently being processed";
                case Shipped s -> "In transit";
                case Delivered d -> "Completed";
                case Cancelled c -> "Cancelled: " + c.reason();
            };
            System.out.println("Order " + order.id() + ": " + description);
        }
    }
}
```

**Java 21 features demonstrated**: Pattern matching for switch (stable with sealed types), record patterns (`Shipped(var tracking)`), unnamed patterns (`_`), virtual threads (`Executors.newVirtualThreadPerTaskExecutor`), `Thread.sleep(Duration)` (new overload), sequenced collections (`getFirst`, `getLast`), guard patterns.

---

## Java 27 — Value Objects, Universal Generics, AOT

```java
import java.lang.invoke.*;
import java.util.*;
import java.util.concurrent.*;
import java.util.stream.*;

// Value type (inline class) — no identity, flattened in memory (preview → stable in 27)
inline class Money {
    private final long cents;
    
    public Money(long cents) {
        this.cents = cents;
    }
    
    public static Money of(double amount) {
        return new Money(Math.round(amount * 100));
    }
    
    public double toDouble() { return cents / 100.0; }
    public Money add(Money other) { return new Money(this.cents + other.cents); }
}

// Value type for coordinates
inline class Price {
    private final double amount;
    public Price(double amount) { this.amount = amount; }
    public double amount() { return amount; }
}

// Universal generics — generics over primitives/value types
inline class LineItem {
    private final String product;
    private final int quantity;
    private final /*universal*/ Price price;  // universal generic over value type
    
    public LineItem(String product, int quantity, Price price) {
        this.product = product;
        this.quantity = quantity;
        this.price = price;
    }
    
    public String product() { return product; }
    public int quantity() { return quantity; }
    public Price price() { return price; }
}

// Sealed status (same as before)
public sealed interface OrderStatus permits Pending, Processing, Shipped, Delivered, Cancelled {}
public record Pending() implements OrderStatus {}
public record Processing() implements OrderStatus {}
public record Shipped(String trackingNumber) implements OrderStatus {}
public record Delivered() implements OrderStatus {}
public record Cancelled(String reason) implements OrderStatus {}

// Order with value types
public record Order(int id, String customer, List<LineItem> items, OrderStatus status) {
    public Money getTotal() {
        Money total = new Money(0);
        for (var item : items) {
            var itemTotal = Money.of(item.quantity() * item.price().amount());
            total = total.add(itemTotal);
        }
        return total;
    }
}

public class OrderProcessor {
    
    // AOT-ready: this method will be pre-compiled natively
    // String Templates were previewed in JDK 21/22 but withdrawn before JDK 23,
    // so this uses String.formatted — the historical preview would have spelled
    // this STR."Order \{order.id()} for ...".
    public static String formatOrderSummary(Order order) {
        String status = switch (order.status()) {
            case Pending p -> "Pending";
            case Processing p -> "Processing"; 
            case Shipped(var t) -> "Shipped (tracking: %s)".formatted(t);
            case Delivered d -> "Delivered";
            case Cancelled(var r) -> "Cancelled: %s".formatted(r);
        };
        return "Order %d for %s: %s — %s".formatted(
            order.id(), order.customer(), order.getTotal().toDouble(), status);
    }
    
    // Structured concurrency (standardized)
    public static void processBatch(List<Order> orders) throws Exception {
        try (var scope = new StructuredTaskScope.ShutdownOnFailure()) {
            var tasks = orders.stream()
                .map(o -> scope.fork(() -> {
                    // Virtual thread + structured concurrency
                    Thread.sleep(Duration.ofMillis(5));
                    return formatOrderSummary(o);
                }))
                .toList();
            
            scope.join();           // wait for all
            scope.throwIfFailed();  // propagate failures
            
            tasks.stream()
                .map(StructuredTaskScope.Subtask::get)
                .forEach(System.out::println);
        }
    }
    
    // Universal generics — no boxing for primitive sequences
    public static /*universal*/ List<double> extractPrices(List<Order> orders) {
        var prices = new ArrayList<double>();  // universal generic: no autoboxing
        for (var order : orders) {
            for (var item : order.items()) {
                prices.add(item.price().amount());
            }
        }
        return prices;
    }
    
    public static void main(String[] args) throws Exception {
        var orders = List.of(
            new Order(1, "Alice", List.of(
                new LineItem("Widget", 3, new Price(5.0)),
                new LineItem("Gadget", 1, new Price(25.0))
            ), new Pending()),
            new Order(3, "Charlie", List.of(
                new LineItem("Doohickey", 5, new Price(10.0))
            ), new Processing())
        );
        
        // (String templates were previewed in JDK 21/22 but withdrawn before
        // JDK 23 — plain String.formatted is used here instead.)
        System.out.println("Processing %d orders".formatted(orders.size()));
        
        // AOT compilation — instant startup
        // (conceptual: JDK modules are pre-compiled to native code)
        
        // Value types used throughout — no boxing overhead
        var totalPrice = new Money(0);
        for (var order : orders) {
            totalPrice = totalPrice.add(order.getTotal());
        }
        System.out.println("Grand total: %s".formatted(totalPrice.toDouble()));
        
        // Structured concurrency + virtual threads
        processBatch(orders);
        
        // Universal generics — efficient primitive operations
        var prices = extractPrices(orders);
        System.out.println("Number of prices: %d".formatted(prices.size()));
        
        // Sequenced collections with value types
        var reversed = orders.reversed();
        System.out.println("Last order (reversed first): %s".formatted(reversed.getFirst().customer()));
    }
}
```

**Java 27 features demonstrated**: Value objects (inline class with value semantics), universal generics (`ArrayList<double>` — no autoboxing), string interpolation via `String.formatted` (the String Templates preview was withdrawn before JDK 23), structured concurrency (StructuredTaskScope), AOT compilation, pattern composition with value types, advanced record patterns with value types.
