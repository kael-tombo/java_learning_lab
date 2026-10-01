package com.learning.database;

import java.sql.*;
import java.time.LocalDateTime;
import java.util.ArrayDeque;
import java.util.Deque;

public class Lab {

    private static final String URL = "jdbc:h2:mem:labdb;DB_CLOSE_DELAY=-1";
    private static final String USER = "sa";
    private static final String PASSWORD = "";

    public static void main(String[] args) throws Exception {
        System.out.println("=== JDBC Database Lab ===");

        initSchema();
        crudOperations();
        batchProcessing();
        transactionDemo();
        metadataDemo();
        connectionPooling();
        cleanUp();
    }

    static void initSchema() throws SQLException {
        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             Statement stmt = conn.createStatement()) {
            stmt.execute("""
                CREATE TABLE IF NOT EXISTS employees (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    department VARCHAR(50),
                    salary DECIMAL(10,2),
                    hired_date DATE
                )
            """);
            System.out.println("Schema initialized.");
        }
    }

    static void crudOperations() throws SQLException {
        System.out.println("\n--- CRUD Operations ---");

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD)) {
            // CREATE
            String insertSQL = "INSERT INTO employees (name, department, salary, hired_date) VALUES (?, ?, ?, ?)";
            try (PreparedStatement ps = conn.prepareStatement(insertSQL, Statement.RETURN_GENERATED_KEYS)) {
                ps.setString(1, "Alice Johnson");
                ps.setString(2, "Engineering");
                ps.setDouble(3, 95000.00);
                ps.setDate(4, Date.valueOf("2023-06-15"));
                ps.executeUpdate();

                ResultSet keys = ps.getGeneratedKeys();
                if (keys.next()) System.out.println("Inserted employee id: " + keys.getInt(1));

                ps.setString(1, "Bob Smith");
                ps.setString(2, "Marketing");
                ps.setDouble(3, 72000.00);
                ps.setDate(4, Date.valueOf("2024-01-10"));
                ps.executeUpdate();
                keys = ps.getGeneratedKeys();
                if (keys.next()) System.out.println("Inserted employee id: " + keys.getInt(1));
            }

            // READ
            try (Statement stmt = conn.createStatement();
                 ResultSet rs = stmt.executeQuery("SELECT * FROM employees")) {
                while (rs.next()) {
                    System.out.printf("  %d | %s | %s | $%.2f | %s%n",
                        rs.getInt("id"), rs.getString("name"),
                        rs.getString("department"), rs.getDouble("salary"),
                        rs.getDate("hired_date"));
                }
            }

            // UPDATE
            try (PreparedStatement ps = conn.prepareStatement(
                    "UPDATE employees SET salary = ? WHERE name = ?")) {
                ps.setDouble(1, 98000.00);
                ps.setString(2, "Alice Johnson");
                int updated = ps.executeUpdate();
                System.out.println("Updated " + updated + " row(s)");
            }

            // DELETE
            try (PreparedStatement ps = conn.prepareStatement(
                    "DELETE FROM employees WHERE name = ?")) {
                ps.setString(1, "Bob Smith");
                int deleted = ps.executeUpdate();
                System.out.println("Deleted " + deleted + " row(s)");
            }
        }
    }

    static void batchProcessing() throws SQLException {
        System.out.println("\n--- Batch Processing ---");

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             PreparedStatement ps = conn.prepareStatement(
                 "INSERT INTO employees (name, department, salary, hired_date) VALUES (?, ?, ?, ?)")) {

            String[][] data = {
                {"Carol Davis", "Engineering", "85000", "2024-03-01"},
                {"Diana Evans", "HR", "65000", "2024-04-15"},
                {"Eve Foster", "Engineering", "92000", "2024-05-20"},
                {"Frank Green", "Marketing", "70000", "2024-06-01"}
            };

            for (String[] row : data) {
                ps.setString(1, row[0]);
                ps.setString(2, row[1]);
                ps.setDouble(3, Double.parseDouble(row[2]));
                ps.setDate(4, Date.valueOf(row[3]));
                ps.addBatch();
            }

            int[] results = ps.executeBatch();
            System.out.println("Batch inserted " + results.length + " employees");
        }
    }

    static void transactionDemo() throws SQLException {
        System.out.println("\n--- Transaction Management ---");

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD)) {
            conn.setAutoCommit(false);
            conn.setTransactionIsolation(Connection.TRANSACTION_READ_COMMITTED);

            try (Statement stmt = conn.createStatement()) {
                stmt.execute("CREATE TABLE IF NOT EXISTS accounts (id INT PRIMARY KEY, owner VARCHAR(50), balance DECIMAL(12,2))");
                stmt.execute("MERGE INTO accounts KEY(id) VALUES (1, 'Alice', 5000.00)");
                stmt.execute("MERGE INTO accounts KEY(id) VALUES (2, 'Bob', 3000.00)");

                String debit = "UPDATE accounts SET balance = balance - ? WHERE id = ? AND balance >= ?";
                String credit = "UPDATE accounts SET balance = balance + ? WHERE id = ?";

                try (PreparedStatement debitPs = conn.prepareStatement(debit);
                     PreparedStatement creditPs = conn.prepareStatement(credit)) {

                    debitPs.setDouble(1, 500.00);
                    debitPs.setInt(2, 1);
                    debitPs.setDouble(3, 500.00);
                    int rows = debitPs.executeUpdate();
                    if (rows != 1) throw new SQLException("Insufficient funds");

                    creditPs.setDouble(1, 500.00);
                    creditPs.setInt(2, 2);
                    creditPs.executeUpdate();

                    conn.commit();
                    System.out.println("Transfer committed successfully");
                }

                try (ResultSet rs = stmt.executeQuery("SELECT * FROM accounts")) {
                    while (rs.next()) {
                        System.out.printf("  Account %d (%s): $%.2f%n",
                            rs.getInt("id"), rs.getString("owner"), rs.getDouble("balance"));
                    }
                }

            } catch (SQLException e) {
                conn.rollback();
                System.err.println("Transaction rolled back: " + e.getMessage());
            } finally {
                conn.setAutoCommit(true);
            }
        }
    }

    static void metadataDemo() throws SQLException {
        System.out.println("\n--- Database & ResultSet Metadata ---");

        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD)) {
            DatabaseMetaData dbMeta = conn.getMetaData();
            System.out.println("DB Product: " + dbMeta.getDatabaseProductName());
            System.out.println("DB Version: " + dbMeta.getDatabaseProductVersion());
            System.out.println("Driver: " + dbMeta.getDriverName());
            System.out.println("JDBC Version: " + dbMeta.getJDBCMajorVersion() + "." + dbMeta.getJDBCMinorVersion());
            System.out.println("Supports transactions: " + dbMeta.supportsTransactions());

            try (Statement stmt = conn.createStatement();
                 ResultSet rs = stmt.executeQuery("SELECT * FROM employees WHERE 1=0")) {
                ResultSetMetaData rsMeta = rs.getMetaData();
                System.out.println("\nEmployees table columns:");
                for (int i = 1; i <= rsMeta.getColumnCount(); i++) {
                    System.out.printf("  %s (%s)%n", rsMeta.getColumnName(i), rsMeta.getColumnTypeName(i));
                }
            }
        }
    }

    static void connectionPooling() {
        System.out.println("\n--- Connection Pool Simulation ---");

        Deque<Connection> pool = new ArrayDeque<>();
        int poolSize = 3;
        try {
            for (int i = 0; i < poolSize; i++) {
                pool.push(DriverManager.getConnection(URL, USER, PASSWORD));
            }
            System.out.println("Pool created with " + pool.size() + " connections");

            Connection conn = pool.poll();
            System.out.println("Borrowed connection: " + conn.getMetaData().getURL());
            pool.offer(conn);
            System.out.println("Returned connection to pool");

            pool.forEach(c -> { try { c.close(); } catch (SQLException ignored) {} });
        } catch (SQLException e) {
            System.err.println("Pool error: " + e.getMessage());
        }
    }

    static void cleanUp() throws SQLException {
        try (Connection conn = DriverManager.getConnection(URL, USER, PASSWORD);
             Statement stmt = conn.createStatement()) {
            stmt.execute("DROP TABLE employees IF EXISTS");
            stmt.execute("DROP TABLE accounts IF EXISTS");
            System.out.println("\nCleanup complete.");
        }
    }
}
