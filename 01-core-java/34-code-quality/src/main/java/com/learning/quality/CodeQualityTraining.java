package com.learning.quality;

import java.util.*;

public class CodeQualityTraining {

    public static void main(String[] args) {
        System.out.println("=== Module 34: Code Quality and Clean Code ===");
        System.out.println("Learning Objective: Write maintainable, readable, testable code");

        demonstrateCleanCodePrinciples();
        demonstrateRefactoringTechniques();
        demonstrateCodeSmells();
        demonstrateStaticAnalysis();
        runExercises();
        runQuizzes();
    }

    private static void demonstrateCleanCodePrinciples() {
        System.out.println("\n=== CLEAN CODE PRINCIPLES ===");

        System.out.println("\n1. Meaningful Names:");
        System.out.println("   ✓ Use intent-revealing names: int d vs int daysSinceCreation");
        System.out.println("   ✓ Avoid magic numbers: use constants");
        System.out.println("   ✓ Use pronounceable names: not genymdhms");
        System.out.println("   ✓ Use searchable names: not single-letter except loops");

        System.out.println("\n2. Functions:");
        System.out.println("   ✓ Small: 20-30 lines max");
        System.out.println("   ✓ Do one thing well");
        System.out.println("   ✓ Use descriptive names");
        System.out.println("   ✓ Prefer fewer arguments (0-3 ideal)");
        System.out.println("   ✓ No side effects");

        System.out.println("\n3. Comments:");
        System.out.println("   ✗ Don't explain bad code with comments - fix the code");
        System.out.println("   ✓ Explain WHY, not WHAT");
        System.out.println("   ✓ Use Javadoc for public APIs");
        System.out.println("   ✓ TODO comments for future work");

        System.out.println("\n4. Formatting:");
        System.out.println("   ✓ Consistent indentation");
        System.out.println("   ✓ Group related code together");
        System.out.println("   ✓ Limit line length (100-120 chars)");
        System.out.println("   ✓ Use blank lines to separate concerns");

        System.out.println("\n5. Error Handling:");
        System.out.println("   ✓ Use exceptions, not return codes");
        System.out.println("   ✓ Don't return null (use Optional)");
        System.out.println("   ✓ Catch specific exceptions");
        System.out.println("   ✓ Log and rethrow appropriately");
    }

    private static void demonstrateRefactoringTechniques() {
        System.out.println("\n=== REFACTORING TECHNIQUES ===");

        System.out.println("\n1. Extract Method:");
        String extract = """
            // BEFORE
            void printInvoice() {
                System.out.println("Customer: " + customer.getName());
                System.out.println("Address: " + customer.getAddress());
                // 50 more lines of printing
            }

            // AFTER
            void printInvoice() {
                printCustomerInfo();
                printLineItems();
                printTotal();
            }""";
        System.out.println(extract);

        System.out.println("\n2. Rename Variable/Method:");
        String rename = """
            // BEFORE
            int d = 0; // what is d?
            public void calc() { ... }

            // AFTER
            int daysSinceLastOrder = 0;
            public void calculateOrderTotal() { ... }""";
        System.out.println(rename);

        System.out.println("\n3. Replace Conditional with Polymorphism:");
        String polymorphism = """
            // BEFORE
            if (type.equals("PREMIUM")) {
                // premium calculation
            } else if (type.equals("BASIC")) {
                // basic calculation
            }

            // AFTER
            interface PricingStrategy { double calculate(Order o); }
            class PremiumPricing implements PricingStrategy { ... }
            class BasicPricing implements PricingStrategy { ... }""";
        System.out.println(polymorphism);

        System.out.println("\n4. Introduce Parameter Object:");
        String paramObj = """
            // BEFORE
            void createReport(String start, String end, 
                String format, boolean includeCharts) { }

            // AFTER
            class ReportConfig {
                String startDate, endDate;
                String format;
                boolean includeCharts;
            }
            void createReport(ReportConfig config) { }""";
        System.out.println(paramObj);

        System.out.println("\n5. Replace Null with Optional:");
        String optional = """
            // BEFORE
            User user = userService.findById(id);
            if (user != null) {
                process(user);
            }

            // AFTER
            Optional<User> user = userService.findById(id);
            user.ifPresent(this::process);
            // or user.orElseThrow(() -> new NotFoundException());""";
        System.out.println(optional);
    }

    private static void demonstrateCodeSmells() {
        System.out.println("\n=== CODE SMELLS ===");

        System.out.println("\n1. Bloaters (Complex Code):");
        String[] bloaters = {
            "Long Method - extract to smaller methods",
            "Large Class - apply Single Responsibility",
            "Primitive Obsession - use objects for related data",
            "Long Parameter List - use parameter objects"
        };
        for (String b : bloaters) System.out.println("   • " + b);

        System.out.println("\n2. Object-Orientation Abusers:");
        String[] oo = {
            "Switch Statements - use polymorphism",
            "Temporary Field - encapsulate related data",
            "Refused Bequest - honor parent contract or break it"
        };
        for (String o : oo) System.out.println("   • " + o);

        System.out.println("\n3. Change Preventers:");
        String[] change = {
            "Divergent Change - single class has multiple reasons to change",
            "Shotgun Surgery - one change requires many small changes",
            "Parallel Inheritance - mirror class hierarchies"
        };
        for (String c : change) System.out.println("   • " + c);

        System.out.println("\n4. Dispensables (Should be Removed):");
        String[] dispensables = {
            "Duplicate Code - extract to common method",
            "Lazy Class - remove classes that do too little",
            "Data Class - add behavior to classes with only data",
            "Dead Code - delete unused code"
        };
        for (String d : dispensables) System.out.println("   • " + d);

        System.out.println("\n5. Couplers:");
        String[] couplers = {
            "Feature Envy - method uses more of another class than its own",
            "Inappropriate Intimacy - classes know too much about each other",
            "Message Chains - long chain of method calls",
            "Middle Man - delegating class does too little"
        };
        for (String c : couplers) System.out.println("   • " + c);
    }

    private static void demonstrateStaticAnalysis() {
        System.out.println("\n=== STATIC ANALYSIS TOOLS ===");

        System.out.println("\n1. Code Quality Tools:");
        Map<String, String> tools = new LinkedHashMap<>();
        tools.put("SpotBugs", "Finds bugs, uses FindBugs engine");
        tools.put("PMD", "Copies, dead code, empty blocks");
        tools.put("Checkstyle", "Coding standards compliance");
        tools.put("SonarQube", "Comprehensive platform");
        tools.forEach((k, v) -> System.out.printf("   %-15s: %s%n", k, v));

        System.out.println("\n2. Maven Configuration:");
        String config = """
            <build>
              <plugins>
                <plugin>
                  <groupId>org.apache.maven.plugins</groupId>
                  <artifactId>maven-checkstyle-plugin</artifactId>
                </plugin>
                <plugin>
                  <groupId>com.github.spotbugs</groupId>
                  <artifactId>spotbugs-maven-plugin</artifactId>
                </plugin>
              </plugins>
            </build>""";
        System.out.println(config);

        System.out.println("\n3. Quality Gates (SonarQube):");
        String[] gates = {
            "Coverage > 80%",
            "No new critical bugs",
            "Duplication < 3%",
            "Maintainability rating A",
            "Technical debt ratio < 5%"
        };
        for (String g : gates) System.out.println("   ✓ " + g);

        System.out.println("\n4. Quick Fixes Checklist:");
        String[] fixes = {
            "Run SpotBugs: mvn spotbugs:check",
            "Run Checkstyle: mvn checkstyle:check",
            "Run tests with coverage",
            "Review code complexity",
            "Check for null safety"
        };
        for (String f : fixes) System.out.println("   → " + f);
    }

    private static void runExercises() {
        System.out.println("\n=== EXERCISES ===\n");

        System.out.println("Exercise 1: Identify Code Smells");
        String badCode = """
            class OrderService {
                public void process(String data, int type, 
                    String customer, double amount, boolean urgent,
                    String address, String product, int quantity) {
                    // 200 lines of code
                    if (type == 1) { ... }
                    else if (type == 2) { ... }
                    else if (type == 3) { ... }
                }
            }""";
        System.out.println(badCode);
        System.out.println("  Refactor to: smaller methods, parameter object, polymorphism\n");

        System.out.println("Exercise 2: Clean Up Method");
        System.out.println("  Original: void doIt() { ... }\n");

        System.out.println("Exercise 3: Replace Conditional with Strategy");
        System.out.println("  Use enums/types for calculation logic\n");

        System.out.println("Exercise 4: Add null safety to existing code");
        System.out.println("  Convert null checks to Optional\n");
    }

    private static void runQuizzes() {
        System.out.println("\n=== KNOWLEDGE CHECK ===\n");

        String[][] quizzes = {
            {"What is the recommended maximum size for a method?",
             "50 lines", "20-30 lines", "100 lines", "B"},
            {"Which is NOT a code smell?",
             "Long Method", "Feature Envy", "Clean Code", "C"},
            {"Which tool finds potential bugs in Java?",
             "PMD", "SpotBugs", "Both A and B", "C"},
            {"What should you do with duplicate code?",
             "Leave it", "Copy to multiple places", "Extract to common method", "C"},
            {"Instead of returning null, you should use?",
             "Empty string", "Optional", "Zero", "B"},
            {"What does SOLID help achieve?",
             "Code complexity", "Maintainability", "Long methods", "B"},
            {"Comments should explain WHAT code does?",
             "True", "False - explain WHY", "Only for complex code", "B"},
            {"The 'Feature Envy' smell means a method:",
             "Uses another class more than its own", "Is too small", "Has no tests", "A"}
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
        System.out.println("\nModule 34 Complete!");
        System.out.println("Next: Module 35 - System Design Fundamentals");
    }
}