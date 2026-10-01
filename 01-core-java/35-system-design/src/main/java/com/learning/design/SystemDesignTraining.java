package com.learning.design;

import java.util.*;

public class SystemDesignTraining {

    public static void main(String[] args) {
        System.out.println("=== Module 35: System Design Fundamentals ===");
        System.out.println("Learning Objective: Design scalable, maintainable systems");

        demonstrateArchitecturePatterns();
        demonstrateScalability();
        demonstrateDistributedSystems();
        demonstrateDatabaseDesign();
        runExercises();
        runQuizzes();
    }

    private static void demonstrateArchitecturePatterns() {
        System.out.println("\n=== ARCHITECTURE PATTERNS ===");

        System.out.println("\n1. Monolithic Architecture:");
        String mono = """
            ┌─────────────────────────────┐
            │     Single Deployment       │
            │  ┌─────┐ ┌─────┐ ┌─────┐   │
            │  │Controller Service Dao  │   │
            │  └─────┘ └─────┘ └─────┘   │
            └─────────────────────────────┘
            
            Pros: Simple, easy to debug, low latency
            Cons: Hard to scale, technology lock-in""";
        System.out.println(mono);

        System.out.println("\n2. Microservices Architecture:");
        String micro = """
            ┌──────┐  ┌──────┐  ┌──────┐
            │User  │  │Order │  │Payment│
            │Service│  │Service│  │Service │
            └──────┘  └──────┘  └──────┘
               ↓         ↓         ↓
            ┌────────────────────────┐
            │    API Gateway         │
            └────────────────────────┘
            
            Pros: Independent deploy, polyglot, fault isolation
            Cons: Complexity, data consistency, network latency""";
        System.out.println(micro);

        System.out.println("\n3. Layered Architecture:");
        String layered = """
            Presentation Layer (Controllers)
                    ↓
            Business Layer (Services)
                    ↓
            Data Access Layer (Repositories)
                    ↓
            Database""";
        System.out.println(layered);

        System.out.println("\n4. Event-Driven Architecture:");
        String eventDriven = """
            ┌────────┐    Event    ┌────────┐
            │Producer│ ──────────→│Consumer│
            └────────┘            └────────┘
                   ↓                    ↓
               ┌────────────────────────┐
               │    Message Broker     │
               │    (Kafka, RabbitMQ)   │
               └────────────────────────┘""";
        System.out.println(eventDriven);
    }

    private static void demonstrateScalability() {
        System.out.println("\n=== SCALABILITY ===");

        System.out.println("\n1. Horizontal vs Vertical Scaling:");
        String[] scaling = {
            "Vertical: Add more CPU/RAM to existing server",
            "Horizontal: Add more servers to handle load",
            "Vertical: Simple, limited by hardware max",
            "Horizontal: Complex, requires stateless design"
        };
        for (String s : scaling) System.out.println("  " + s);

        System.out.println("\n2. Load Balancing Strategies:");
        Map<String, String> lb = new LinkedHashMap<>();
        lb.put("Round Robin", "Sequential distribution");
        lb.put("Least Connections", "Route to fewest active");
        lb.put("IP Hash", "Same client same server");
        lb.put("Weighted", "Based on server capacity");
        lb.put("Least Response Time", "Fastest response wins");
        lb.forEach((k, v) -> System.out.printf("  %-25s: %s%n", k, v));

        System.out.println("\n3. Caching Strategies:");
        String[] cache = {
            "Cache-Aside: App manages cache (Redis pattern)",
            "Write-Through: Write to cache and DB together",
            "Write-Behind: Async DB writes",
            "Refresh-Ahead: Expire before actual expiry"
        };
        for (String c : cache) System.out.println("  ✓ " + c);

        System.out.println("\n4. Database Scaling:");
        String[] dbScale = {
            "Read Replicas: Distribute read load",
            "Sharding: Partition data across servers",
            "Partitioning: Split by key ranges",
            "Denormalization: Optimize for read performance"
        };
        for (String d : dbScale) System.out.println("  " + d);

        System.out.println("\n5. CAP Theorem Trade-offs:");
        System.out.println("  Consistency + Availability (CA): Traditional RDBMS");
        System.out.println("  Consistency + Partition (CP): MongoDB, HBase");
        System.out.println("  Availability + Partition (AP): Cassandra, DynamoDB");
    }

    private static void demonstrateDistributedSystems() {
        System.out.println("\n=== DISTRIBUTED SYSTEMS ===");

        System.out.println("\n1. Communication Patterns:");
        String[] comms = {
            "Synchronous (REST, gRPC) - request/response",
            "Asynchronous (Message Queues) - fire and forget",
            "Streaming (Kafka) - continuous data flow"
        };
        for (String c : comms) System.out.println("  ✓ " + c);

        System.out.println("\n2. Service Discovery:");
        String[] discovery = {
            "Client-side: Eureka, Consul (client queries registry)",
            "Server-side: Load balancer routes to services",
            "DNS-based: Route53, CoreDNS for service names"
        };
        for (String d : discovery) System.out.println("  " + d);

        System.out.println("\n3. Fault Tolerance Patterns:");
        String[] fault = {
            "Circuit Breaker: Prevent cascade failures",
            "Retry with Backoff: Reattempt failed requests",
            "Bulkhead: Isolate failures to specific areas",
            "Dead Letter Queue: Handle failed messages"
        };
        for (String f : fault) System.out.println("  " + f);

        System.out.println("\n4. Consistency Models:");
        String[] consistency = {
            "Strong: All reads see most recent write",
            "Eventual: Updates propagate asynchronously",
            "Causal: Respect cause-effect ordering",
            "Read Your Writes: See your own writes immediately"
        };
        for (String c : consistency) System.out.println("  ✓ " + c);

        System.out.println("\n5. Distributed Tracing:");
        String trace = """
            Trace ID: abc123 (spans request lifecycle)
            ├── [0ms] api-gateway - received request
            ├── [5ms] user-service - validation
            ├── [10ms] user-db - query
            ├── [15ms] order-service - processing
            └── [30ms] response sent""";
        System.out.println(trace);
    }

    private static void demonstrateDatabaseDesign() {
        System.out.println("\n=== DATABASE DESIGN ===");

        System.out.println("\n1. SQL vs NoSQL:");
        Map<String, String> db = new LinkedHashMap<>();
        db.put("SQL (PostgreSQL)", "ACID, relations, complex queries");
        db.put("NoSQL (MongoDB)", "Flexible schema, high write throughput");
        db.put("Key-Value (Redis)", "Fast lookups, caching");
        db.put("Wide-Column (Cassandra)", "Time-series, massive scale");
        db.put("Graph (Neo4j)", "Relationship-heavy data");
        db.forEach((k, v) -> System.out.printf("  %-20s: %s%n", k, v));

        System.out.println("\n2. Data Modeling Steps:");
        String[] steps = {
            "1. Identify entities and relationships",
            "2. Define attributes and constraints",
            "3. Normalize to reduce redundancy",
            "4. Denormalize for performance",
            "5. Define indexes for queries"
        };
        for (String s : steps) System.out.println("  " + s);

        System.out.println("\n3. Normalization Forms:");
        String[] norms = {
            "1NF: Atomic values, no repeating groups",
            "2NF: No partial dependencies",
            "3NF: No transitive dependencies",
            "BCNF: Every determinant is a key"
        };
        for (String n : norms) System.out.println("  " + n);

        System.out.println("\n4. Indexing Strategies:");
        String[] index = {
            "B-Tree: Range queries, sorted data",
            "Hash: Exact match lookups",
            "Full-text: Search within text",
            "Composite: Multiple column queries"
        };
        for (String i : index) System.out.println("  ✓ " + i);

        System.out.println("\n5. Common Design Mistakes:");
        String[] mistakes = {
            "Missing proper indexes",
            "Storing large blobs in database",
            "No pagination for large results",
            "N+1 query problems",
            "Missing foreign key constraints"
        };
        for (String m : mistakes) System.out.println("  ✗ " + m);
    }

    private static void runExercises() {
        System.out.println("\n=== SYSTEM DESIGN EXERCISES ===\n");

        System.out.println("Exercise 1: Design a URL Shortener");
        System.out.println("  Requirements: Create short URLs, redirect to long, track clicks");
        System.out.println("  Consider: Storage, hash function, redirection, analytics\n");

        System.out.println("Exercise 2: Design a Twitter Clone");
        System.out.println("  Requirements: Post tweets, follow users, timeline");
        System.out.println("  Consider: Feed generation, write vs read optimization\n");

        System.out.println("Exercise 3: Design a Parking Lot System");
        System.out.println("  Requirements: Park cars, available spots, billing");
        System.out.println("  Consider: Real-time updates, payment integration\n");

        System.out.println("Exercise 4: Design a Uber-like Service");
        System.out.println("  Requirements: Book rides, driver matching, tracking");
        System.out.println("  Consider: Geolocation, matching algorithm, pricing\n");

        System.out.println("Design Tips:");
        String[] tips = {
            "Start with requirements and constraints",
            "Identify core components and data flow",
            "Consider scalability from start",
            "Sketch architecture diagram first",
            "Discuss trade-offs with interviewer"
        };
        for (String t : tips) System.out.println("  ★ " + t);
    }

    private static void runQuizzes() {
        System.out.println("\n=== KNOWLEDGE CHECK ===\n");

        String[][] quizzes = {
            {"Which scaling adds more servers to the pool?",
             "Vertical", "Horizontal", "Diagonal", "B"},
            {"CAP theorem states you can only have 2 of 3:",
             "Consistency, Availability, Partition", "Cache, API, DB", "Read, Write, Update", "A"},
            {"Which pattern prevents cascade failures?",
             "Retry", "Circuit Breaker", "Load Balancer", "B"},
            {"Which is a NoSQL database?",
             "PostgreSQL", "MySQL", "MongoDB", "C"},
            {"Eventual consistency means:",
             "All reads see same data", "Updates propagate eventually", "No updates allowed", "B"},
            {"Read replicas help with:",
             "Write throughput", "Read throughput", "Data consistency", "B"},
            {"API Gateway handles:",
             "Business logic", "Routing, auth, rate limiting", "Database queries", "B"},
            {"Microservices communicate via:",
             "Direct database access", "Network APIs/messages", "Shared file system", "B"}
        };

        int correct = 0;
        for (int i = 0; i < quizzes.length; i++) {
            System.out.println("Q" + (i + 1) + ": " + quizzes[i][0]);
            System.out.println("  A) " + quizzes[i][1]);
            System.out.println("  B) " + quizzes[i][2]);
            System.out.println("  C) " + quizzes[i][3]);
            System.out.println("  Answer: " + quizzes[i][4] + ") " + 
                quizzes[i][quizzes[i][4].charAt(0) - 'A' + 1]);
            System.out.println();
            correct++;
        }

        System.out.println("=== Quiz Complete: " + correct + "/" + quizzes.length + " correct ===");
        System.out.println("\n=== Module 35 Complete! ===");
        System.out.println("=== Java Learning Lab Complete! ===");
    }
}