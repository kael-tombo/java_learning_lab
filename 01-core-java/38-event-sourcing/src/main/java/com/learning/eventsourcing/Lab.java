package com.learning.eventsourcing;

import java.time.Instant;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.function.Consumer;
import java.util.stream.Stream;

public class Lab {

    static class Event {
        final String aggregateId;
        final String type;
        final Map<String, Object> data;
        final Instant timestamp;
        final int version;

        Event(String aggregateId, String type, Map<String, Object> data, int version) {
            this.aggregateId = aggregateId;
            this.type = type;
            this.data = data;
            this.timestamp = Instant.now();
            this.version = version;
        }

        public String toString() {
            return String.format("#%d %s [%s] %s", version, type, aggregateId, data);
        }
    }

    static class EventStore {
        final Map<String, List<Event>> store = new ConcurrentHashMap<>();

        void append(String aggregateId, Event event) {
            store.computeIfAbsent(aggregateId, k -> new ArrayList<>()).add(event);
        }

        List<Event> read(String aggregateId) {
            return store.getOrDefault(aggregateId, List.of());
        }

        Stream<Event> allEvents() {
            return store.values().stream().flatMap(List::stream)
                .sorted(Comparator.comparingInt(e -> e.version));
        }
    }

    static class BankAccount {
        private final String id;
        private final EventStore eventStore;
        private int balance;
        private int version;

        BankAccount(String id, EventStore eventStore) {
            this.id = id;
            this.eventStore = eventStore;
            this.version = 0;
        }

        void create(String owner) {
            appendEvent("AccountCreated", Map.of("owner", owner, "balance", 0));
        }

        void deposit(int amount) {
            appendEvent("Deposited", Map.of("amount", amount));
        }

        void withdraw(int amount) {
            var history = eventStore.read(id);
            int bal = 0;
            for (var e : history) {
                if (e.type.equals("Deposited")) bal += (int) e.data.get("amount");
                if (e.type.equals("Withdrawn")) bal -= (int) e.data.get("amount");
            }
            if (bal < amount) throw new IllegalStateException("Insufficient funds");
            appendEvent("Withdrawn", Map.of("amount", amount));
        }

        private void appendEvent(String type, Map<String, Object> data) {
            version++;
            var event = new Event(id, type, new HashMap<>(data), version);
            eventStore.append(id, event);
            if (type.equals("AccountCreated") || type.equals("Deposited")) balance += (int) data.getOrDefault("amount", 0);
            if (type.equals("Withdrawn")) balance -= (int) data.get("amount");
        }

        int getBalance() { return balance; }
    }

    public static void main(String[] args) {
        System.out.println("=== Event Sourcing Lab ===\n");

        eventStoreBasics();
        aggregateReplay();
        snapshotting();
        eventProjection();
        concurrencyControl();
    }

    static void eventStoreBasics() {
        System.out.println("--- Event Store Basics ---");
        var store = new EventStore();

        var acct = new BankAccount("acc-1", store);
        acct.create("Alice");
        acct.deposit(1000);
        acct.withdraw(300);
        acct.deposit(500);

        System.out.println("  Balance: $" + acct.getBalance());
        System.out.println("  Event stream:");
        for (var e : store.read("acc-1")) {
            System.out.println("    " + e);
        }
    }

    static void aggregateReplay() {
        System.out.println("\n--- Aggregate Replay ---");
        var store = new EventStore();

        var acct = new BankAccount("acc-2", store);
        acct.create("Bob");
        acct.deposit(2000);
        acct.withdraw(500);
        System.out.println("  First balance: $" + acct.getBalance());

        var replayed = new BankAccount("acc-2", store);
        for (var e : List.copyOf(store.read("acc-2"))) {
            if (e.type.equals("AccountCreated")) replayed.deposit(0);
            if (e.type.equals("Deposited")) replayed.deposit((int) e.data.get("amount"));
            if (e.type.equals("Withdrawn")) replayed.withdraw((int) e.data.get("amount"));
        }
        System.out.println("  Replayed balance: $" + replayed.getBalance());
    }

    static void snapshotting() {
        System.out.println("\n--- Snapshotting ---");
        System.out.println("  Without snapshots: replay ALL events from origin");
        System.out.println("  With snapshots:    replay FROM last snapshot only");
        System.out.println("  Snapshot strategy: every N events (e.g. every 100)");
        System.out.println("  Snapshot = current state serialized at version X");
    }

    static void eventProjection() {
        System.out.println("\n--- Event Projection ---");
        var store = new EventStore();
        var acct = new BankAccount("acc-3", store);
        acct.create("Carol");
        acct.deposit(5000);
        acct.withdraw(1200);

        var projection = new HashMap<String, Object>();
        projection.put("totalDeposits", 0);
        projection.put("totalWithdrawals", 0);
        projection.put("transactionCount", 0);

        for (var e : store.read("acc-3")) {
            projection.put("transactionCount", (int) projection.get("transactionCount") + 1);
            if (e.type.equals("Deposited")) {
                projection.put("totalDeposits", (int) projection.get("totalDeposits") + (int) e.data.get("amount"));
            }
            if (e.type.equals("Withdrawn")) {
                projection.put("totalWithdrawals", (int) projection.get("totalWithdrawals") + (int) e.data.get("amount"));
            }
        }

        System.out.println("  Projection for acc-3:");
        projection.forEach((k, v) -> System.out.println("    " + k + " = " + v));
    }

    static void concurrencyControl() {
        System.out.println("\n--- Concurrency & Optimistic Locking ---");
        System.out.println("  Expected version check prevents conflicting writes");
        System.out.println("  Event version = aggregate version at write time");
        System.out.println("  If actual version != expected version -> reject (ConcurrencyException)");
        System.out.println("  Retry with fresh read -> rebase -> reapply");
        System.out.println("  Common in CQRS/ES systems like Axon, Eventuate");
    }
}
