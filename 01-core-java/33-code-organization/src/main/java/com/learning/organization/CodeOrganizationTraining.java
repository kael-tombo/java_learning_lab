package com.learning.organization;

import java.util.*;

public class CodeOrganizationTraining {

    public static void main(String[] args) {
        System.out.println("=== Module 33: Code Organization and Best Practices ===");
        System.out.println("Learning Objective: Master project structure, SOLID principles, and clean code");

        demonstratePackageOrganization();
        demonstrateNamingConventions();
        demonstrateSOLIDPrinciples();
        demonstrateProjectStructure();
        runExercises();
        runQuizzes();
    }

    private static void demonstratePackageOrganization() {
        System.out.println("\n=== PACKAGE ORGANIZATION ===");

        System.out.println("\n1. Package by Layer (Traditional):");
        String layer = """
            com.example.app/
            ├── controller/    # HTTP handlers
            ├── service/       # Business logic
            ├── repository/    # Data access
            ├── model/         # Entities
            └── dto/           # Data transfer objects""";
        System.out.println(layer);

        System.out.println("\n2. Package by Feature (Recommended):");
        String feature = """
            com.example.app/
            ├── user/
            │   ├── UserController.java
            │   ├── UserService.java
            │   ├── UserRepository.java
            │   └── User.java
            ├── order/
            │   ├── OrderController.java
            │   ├── OrderService.java
            │   └── Order.java
            └── payment/...""";
        System.out.println(feature);

        System.out.println("\n3. Package Naming Conventions:");
        String[] conventions = {
            "Use lowercase letters (com.example, not com.Example)",
            "Use dots to separate hierarchical levels",
            "Reverse domain name: com.company.project",
            "Avoid reserved words and special characters",
            "Use singular names for packages (user, not users)"
        };
        for (String c : conventions) System.out.println("  ✓ " + c);
    }

    private static void demonstrateNamingConventions() {
        System.out.println("\n=== NAMING CONVENTIONS ===");

        System.out.println("\n1. Classes and Interfaces:");
        String[] classNaming = {
            "Class: UserService, OrderController (PascalCase)",
            "Interface: Repository, Serializable (noun/phrase)",
            "Exception: InvalidInputException (ends with Exception)",
            "Test: UserServiceTest, IntegrationTest (ends with Test)"
        };
        for (String n : classNaming) System.out.println("  ✓ " + n);

        System.out.println("\n2. Methods:");
        String[] methodNaming = {
            "Verb/VerbPhrase: calculateTotal(), findById()",
            "Getters/Setters: getName(), setName()",
            "Boolean: isActive(), hasPermission()",
            "Finders: findByEmail(), searchByKeyword()"
        };
        for (String m : methodNaming) System.out.println("  ✓ " + m);

        System.out.println("\n3. Variables:");
        String[] varNaming = {
            "CamelCase: userName, orderList, maxCount",
            "Constants: MAX_RETRY_COUNT, DEFAULT_TIMEOUT",
            "Loop variables: i, j, k (short), item, element (meaningful)",
            "Avoid: single chars except in loops, abbreviations"
        };
        for (String v : varNaming) System.out.println("  ✓ " + v);

        System.out.println("\n4. Naming Examples - Good vs Bad:");
        Map<String, String> examples = new LinkedHashMap<>();
        examples.put("UserService", "userSvc (avoid abbreviations)");
        examples.put("calculateTotalOrderAmount", "calc()");
        examples.put("isUserActive", "active");
        examples.put("MAX_RETRY_COUNT", "maxRetry");
        examples.put("userList", "users, userList (both OK)");

        examples.forEach((good, bad) ->
            System.out.printf("  ✓ %-30s | ✗ %s%n", good, bad));
    }

    private static void demonstrateSOLIDPrinciples() {
        System.out.println("\n=== SOLID PRINCIPLES ===");

        System.out.println("\nS - Single Responsibility Principle:");
        String srp = """
            // BAD - Multiple responsibilities
            class UserManager {
                void saveUser() { }      // persistence
                void validateUser() { } // validation
                void sendEmail() { }     // notification
            }

            // GOOD - Single responsibility each
            class UserService { void saveUser() { } }
            class UserValidator { void validate() { } }
            class EmailService { void send() { } }""";
        System.out.println(srp);

        System.out.println("\nO - Open/Closed Principle:");
        String ocp = """
            // Open for extension, closed for modification
            abstract class Shape {
                abstract double area();
            }

            class Circle extends Shape {
                double radius;
                double area() { return Math.PI * radius * radius; }
            }

            class Rectangle extends Shape {
                double width, height;
                double area() { return width * height; }
            }""";
        System.out.println(ocp);

        System.out.println("\nL - Liskov Substitution Principle:");
        String lsp = """
            // Subtypes must be substitutable for base types
            abstract class Bird {
                abstract void fly();
            }

            // BAD - Penguin can't fly but inherits fly()
            class Penguin extends Bird {
                void fly() { throw new UnsupportedOperationException(); }
            }

            // GOOD - Separate interface
            interface FlyingBird { void fly(); }
            interface SwimmingBird { void swim(); }""";
        System.out.println(lsp);

        System.out.println("\nI - Interface Segregation Principle:");
        String isp = """
            // BAD - Fat interface
            interface Worker {
                void work();
                void eat();
                void sleep();
            }

            // GOOD - Small, focused interfaces
            interface Workable { void work(); }
            interface Eatable { void eat(); }
            interface Sleepable { void sleep(); }""";
        System.out.println(isp);

        System.out.println("\nD - Dependency Inversion Principle:");
        String dip = """
            // BAD - High-level depends on low-level
            class EmailNotifier {
                void notify() { /* email logic */ }
            }
            class UserService {
                private EmailNotifier notifier;
            }

            // GOOD - Depend on abstractions
            interface Notifier { void notify(String msg); }
            class EmailNotifier implements Notifier { ... }
            class UserService {
                private Notifier notifier; // depends on interface
            }""";
        System.out.println(dip);
    }

    private static void demonstrateProjectStructure() {
        System.out.println("\n=== STANDARD PROJECT STRUCTURE ===");

        String structure = """
            project-root/
            ├── src/
            │   ├── main/
            │   │   ├── java/
            │   │   │   └── com/learning/
            │   │   │       ├── config/
            │   │   │       ├── controller/
            │   │   │       ├── service/
            │   │   │       ├── repository/
            │   │   │       ├── model/
            │   │   │       └── util/
            │   │   └── resources/
            │   │       ├── application.yml
            │   │       └── static/
            │   └── test/
            │       ├── java/.../
            │       └── resources/
            ├── pom.xml
            └── README.md""";
        System.out.println(structure);

        System.out.println("\nKey Directory Purposes:");
        Map<String, String> dirs = new LinkedHashMap<>();
        dirs.put("config/", "Configuration classes");
        dirs.put("controller/", "HTTP request handlers");
        dirs.put("service/", "Business logic");
        dirs.put("repository/", "Data access");
        dirs.put("model/", "Domain entities");
        dirs.put("dto/", "Data transfer objects");
        dirs.put("util/", "Utility classes");
        dirs.put("exception/", "Custom exceptions");
        dirs.forEach((k, v) -> System.out.printf("  %-15s %s%n", k, v));
    }

    private static void runExercises() {
        System.out.println("\n=== EXERCISES ===");

        String[] exercises = {
            "1. Refactor a class with 3 responsibilities into separate classes",
            "2. Create an interface with 5 methods, then implement with 2 focused interfaces",
            "3. Fix a Liskov Substitution violation in inheritance hierarchy",
            "4. Apply Dependency Injection to replace direct instantiation",
            "5. Organize 10 related classes into proper packages by feature"
        };

        System.out.println("\nPractice Exercises:");
        for (String ex : exercises) {
            System.out.println("  " + ex);
        }

        System.out.println("\nExercise Solutions:");
        System.out.println("  [See: RefactoredUserService.java]");
    }

    private static void runQuizzes() {
        System.out.println("\n=== KNOWLEDGE CHECK ===\n");

        String[][] quizzes = {
            {"Which principle states 'classes should have one reason to change'?",
             "Single Responsibility", "Open/Closed", "Liskov Substitution", "A"},
            {"What is the recommended package structure for large applications?",
             "Layer-based", "Feature-based", "Hybrid", "B"},
            {"Which naming convention is correct for constants?",
             "maxRetryCount", "max_retry_count", "MAX_RETRY_COUNT", "C"},
            {"What does SOLID stand for?",
             "Simple Object Oriented Design", "Single Interface Double",
             "Single-Responsibility, Open-Closed, Liskov, Interface-Segregation, Dependency-Inversion", "C"},
            {"Which principle says 'depend on abstractions, not concretions'?",
             "Single Responsibility", "Dependency Inversion", "Interface Segregation", "B"}
        };

        int correct = 0;
        for (int i = 0; i < quizzes.length; i++) {
            System.out.println("Q" + (i + 1) + ": " + quizzes[i][0]);
            System.out.println("  A) " + quizzes[i][1]);
            System.out.println("  B) " + quizzes[i][2]);
            System.out.println("  C) " + quizzes[i][3]);
            System.out.println("  Answer: " + quizzes[i][4] + ") " + quizzes[i][quizzes[i][4].charAt(0) - 'A' + 1]);
            System.out.println();
            correct++;
        }

        System.out.println("Quiz Complete! " + correct + "/" + quizzes.length + " correct");
        System.out.println("\n=== Module 33 Complete ===");
        System.out.println("Next: Module 34 - Code Quality & Clean Code");
    }
}