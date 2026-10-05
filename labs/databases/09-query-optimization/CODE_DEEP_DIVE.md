# Query Optimization — Code Deep Dive

## Layered architecture
```
Client → JDBC/JPA → Driver → Network → Database Engine → Storage
```

## Key code paths
### Path 1: query optimization request lifecycle
```java
// Query Optimization — path 1
try (Connection c = ds.getConnection();
     PreparedStatement ps = c.prepareStatement(sql)) {
    ps.setFetchSize(200);
    ResultSet rs = ps.executeQuery();
    while (rs.next()) { /* materialize */ }
}
```
Notes: watch for N+1 queries, missing fetch size, and unclosed resources.

### Path 2: query optimization request lifecycle
```java
// Query Optimization — path 2
try (Connection c = ds.getConnection();
     PreparedStatement ps = c.prepareStatement(sql)) {
    ps.setFetchSize(200);
    ResultSet rs = ps.executeQuery();
    while (rs.next()) { /* materialize */ }
}
```
Notes: watch for N+1 queries, missing fetch size, and unclosed resources.

### Path 3: query optimization request lifecycle
```java
// Query Optimization — path 3
try (Connection c = ds.getConnection();
     PreparedStatement ps = c.prepareStatement(sql)) {
    ps.setFetchSize(200);
    ResultSet rs = ps.executeQuery();
    while (rs.next()) { /* materialize */ }
}
```
Notes: watch for N+1 queries, missing fetch size, and unclosed resources.

### Path 4: query optimization request lifecycle
```java
// Query Optimization — path 4
try (Connection c = ds.getConnection();
     PreparedStatement ps = c.prepareStatement(sql)) {
    ps.setFetchSize(200);
    ResultSet rs = ps.executeQuery();
    while (rs.next()) { /* materialize */ }
}
```
Notes: watch for N+1 queries, missing fetch size, and unclosed resources.

### Path 5: query optimization request lifecycle
```java
// Query Optimization — path 5
try (Connection c = ds.getConnection();
     PreparedStatement ps = c.prepareStatement(sql)) {
    ps.setFetchSize(200);
    ResultSet rs = ps.executeQuery();
    while (rs.next()) { /* materialize */ }
}
```
Notes: watch for N+1 queries, missing fetch size, and unclosed resources.

### Path 6: query optimization request lifecycle
```java
// Query Optimization — path 6
try (Connection c = ds.getConnection();
     PreparedStatement ps = c.prepareStatement(sql)) {
    ps.setFetchSize(200);
    ResultSet rs = ps.executeQuery();
    while (rs.next()) { /* materialize */ }
}
```
Notes: watch for N+1 queries, missing fetch size, and unclosed resources.

### Path 7: query optimization request lifecycle
```java
// Query Optimization — path 7
try (Connection c = ds.getConnection();
     PreparedStatement ps = c.prepareStatement(sql)) {
    ps.setFetchSize(200);
    ResultSet rs = ps.executeQuery();
    while (rs.next()) { /* materialize */ }
}
```
Notes: watch for N+1 queries, missing fetch size, and unclosed resources.

### Path 8: query optimization request lifecycle
```java
// Query Optimization — path 8
try (Connection c = ds.getConnection();
     PreparedStatement ps = c.prepareStatement(sql)) {
    ps.setFetchSize(200);
    ResultSet rs = ps.executeQuery();
    while (rs.next()) { /* materialize */ }
}
```
Notes: watch for N+1 queries, missing fetch size, and unclosed resources.

- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
- Profiling tip: capture pg_stat_statements / slow query log while running this path.
