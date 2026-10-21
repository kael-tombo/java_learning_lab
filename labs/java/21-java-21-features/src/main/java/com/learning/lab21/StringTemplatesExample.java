package com.learning.lab21;

/**
 * Demonstrates Java 21 string features (text blocks, String.formatted).
 * Note: String templates (STR."...") were previewed in JDK 21/22 and then
 * withdrawn before JDK 23 — no current JDK accepts them, so this class
 * uses String.formatted for interpolation instead.
 */
public class StringTemplatesExample {

    public static void showStringFeatures() {
        System.out.println("=== Java 21 String Features ===");

        String name = "Java";
        int version = 21;

        String formatted = "Welcome to %s %d!".formatted(name, version);
        System.out.println(formatted);

        String repeat = "Java! ".repeat(3);
        System.out.println("Repeat: " + repeat);

        String block = """
                <html>
                    <body>
                        <h1>Java 21</h1>
                    </body>
                </html>
                """;
        System.out.println("Text block:\n" + block);
    }
}
